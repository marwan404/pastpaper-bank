import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

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

class Task(BaseModel):
    name: str
    done: bool

class Tasks(BaseModel):
    tasks: list[Task]

tasks_list = []
tasks = Tasks(tasks=tasks_list)

with open("tasks.json", "w") as f:
    json.dump(tasks.model_dump(), f, indent=4)


@app.get("/tasks", response_model=Tasks)
def get_tasks():
    with open("tasks.json", "r") as file:
        data = json.load(file)
    return data

@app.post("/tasks", response_model=Task)
def add_task(task: Task):
    with open("tasks.json", "r+") as json_file:
        data = json.load(json_file)
        data["tasks"].append(task.model_dump())
        json_file.seek(0)
        json.dump(data, json_file, indent=4)
        json_file.truncate()
    return task


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)