import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio

app = FastAPI()

connections = []

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskCreate(BaseModel):
    name: str

class Task(BaseModel):
    id: int
    name: str
    done: bool

class Tasks(BaseModel):
    tasks: list[Task]


def get_next_id(tasks: list[dict]) -> int:
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connections.remove(ws)


@app.get("/tasks", response_model=Tasks)
def get_tasks():
    with open("tasks.json", "r") as file:
        data = json.load(file)
    return data


@app.post("/tasks", response_model=Task)
def add_task(task: TaskCreate):
    with open("tasks.json", "r+") as f:
        data = json.load(f)

        new_task = {
            "id": get_next_id(data["tasks"]),
            "name": task.name,
            "done": False
        }

        data["tasks"].append(new_task)

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

    return new_task


@app.put("/tasks/{task_id}/toggle")
async def toggle_task(task_id: int):
    with open("tasks.json", "r") as f:
        data = json.load(f)

    for task in data["tasks"]:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            new_state = task["done"]
            break
    else:
        raise HTTPException(status_code=404, detail="Task not found")

    with open("tasks.json", "w") as f:
        json.dump(data, f, indent=4)

    for ws in connections:
        await ws.send_text("task_updated")

    return {"done": new_state}


@app.put("/tasks/{task_id}/change")
async def complete_task(task_id: int, task_name: str):
    with open("tasks.json", "r") as f:
        data = json.load(f)

    for task in data["tasks"]:
        if task["id"] == task_id:
            task["name"] = task_name
            break
    else:
        raise HTTPException(status_code=404, detail="Task not found")

    with open("tasks.json", "w") as f:
        json.dump(data, f, indent=4)

    for ws in connections:
        await ws.send_text("task_updated")

    return {"message": "Task updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)