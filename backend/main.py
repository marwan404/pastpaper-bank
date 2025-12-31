import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    file_path = "files/hello.html"
    return FileResponse(file_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)