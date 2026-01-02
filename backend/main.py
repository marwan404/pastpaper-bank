import json
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ------------------------
# CORS CONFIG
# ------------------------
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # allow all for dev
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# MODELS
# ------------------------
class TaskCreate(BaseModel):
    name: str


class Task(BaseModel):
    id: int
    name: str
    done: bool


class Tasks(BaseModel):
    tasks: List[Task]


# ------------------------
# GLOBALS
# ------------------------
connections: List[WebSocket] = []
TASKS_FILE = "tasks.json"


# ------------------------
# UTILITY FUNCTIONS
# ------------------------
def get_next_id(tasks: List[dict]) -> int:
    """Return next auto-increment ID for a task."""
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def read_tasks() -> dict:
    """Read tasks.json safely."""
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # create file if missing
        with open(TASKS_FILE, "w") as f:
            json.dump({"tasks": []}, f, indent=4)
        return {"tasks": []}


def write_tasks(data: dict) -> None:
    """Write tasks.json safely."""
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=4)


async def broadcast(message: str) -> None:
    """Send message to all connected WebSockets, remove dead ones."""
    dead_connections = []
    for ws in connections:
        try:
            await ws.send_text(message)
        except WebSocketDisconnect:
            dead_connections.append(ws)
    for ws in dead_connections:
        connections.remove(ws)


# ------------------------
# ROUTES
# ------------------------
@app.get("/tasks", response_model=Tasks)
def get_tasks():
    data = read_tasks()
    return data


@app.post("/tasks", response_model=Task)
async def add_task(task: TaskCreate):
    data = read_tasks()
    new_task = {
        "id": get_next_id(data["tasks"]),
        "name": task.name,
        "done": False,
    }
    data["tasks"].append(new_task)
    write_tasks(data)

    # notify all WebSocket clients
    await broadcast("task_updated")

    return new_task


@app.put("/tasks/{task_id}/toggle")
async def toggle_task(task_id: int):
    data = read_tasks()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            new_state = task["done"]
            break
    else:
        raise HTTPException(status_code=404, detail="Task not found")

    write_tasks(data)
    await broadcast("task_updated")
    return {"done": new_state}


@app.put("/tasks/{task_id}/change")
async def change_task_name(task_id: int, task_name: str = Query(...)):
    data = read_tasks()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["name"] = task_name
            break
    else:
        raise HTTPException(status_code=404, detail="Task not found")

    write_tasks(data)
    await broadcast("task_updated")
    return {"message": "Task updated"}


# ------------------------
# WEBSOCKET
# ------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            await ws.receive_text()  # keep the socket alive
    except WebSocketDisconnect:
        connections.remove(ws)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)