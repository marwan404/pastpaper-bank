import json
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio
from asyncio import Lock


app = FastAPI()
file_lock = Lock()

# ------------------------
# CORS CONFIG
# ------------------------
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
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


async def broadcast(message: str):
    for ws in connections.copy():
        try:
            await ws.send_text(message)
        except (WebSocketDisconnect, RuntimeError, ConnectionResetError):
            connections.remove(ws)


# ------------------------
# ROUTES
# ------------------------
@app.get("/tasks", response_model=Tasks)
async def get_tasks():
    async with file_lock:
        data = read_tasks()
    return data


@app.post("/tasks", response_model=Task)
async def add_task(task: TaskCreate):
    async with file_lock:
        data = read_tasks()
        new_task = {
            "id": get_next_id(data["tasks"]),
            "name": task.name,
            "done": False,
        }
        data["tasks"].append(new_task)
        write_tasks(data)

    await broadcast(json.dumps({
        "event": "task_added",
        "task_id": new_task["id"]
    }))
    return new_task


@app.put("/tasks/{task_id}/toggle")
async def toggle_task(task_id: int):
    async with file_lock:
        data = read_tasks()
        for task in data["tasks"]:
            if task["id"] == task_id:
                task["done"] = not task["done"]
                new_state = task["done"]
                break
        else:
            raise HTTPException(status_code=404, detail="Task not found")

        write_tasks(data)
    await broadcast(json.dumps({
        "event": "task_updated",
        "task_id": task_id
    }))

    return {"done": new_state}


@app.put("/tasks/{task_id}/change")
async def change_task_name(task_id: int, task_name: str = Query(...)):
    async with file_lock:
        data = read_tasks()
        for task in data["tasks"]:
            if task["id"] == task_id:
                task["name"] = task_name
                break
        else:
            raise HTTPException(status_code=404, detail="Task not found")

        write_tasks(data)
    await broadcast(json.dumps({
        "event": "task_updated",
        "task_id": task_id
    }))
    return {"message": "Task updated"}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    async with file_lock:
        data = read_tasks()
        tasks = data["tasks"]

        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                tasks.pop(i)
                break
        else:
            raise HTTPException(status_code=404, detail="Task not found")

        write_tasks(data)
    await broadcast(json.dumps({
        "event": "task_deleted",
        "task_id": task_id
    }))
    return {"message": "Task deleted"}



# ------------------------
# WEBSOCKET
# ------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            await asyncio.sleep(3600)
    except WebSocketDisconnect:
        connections.remove(ws)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)