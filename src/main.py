import logging
import uuid
from datetime import datetime, UTC
import uvicorn
from fastapi import FastAPI
from models import Task, TaskStatus
from task_queue import tasks, queue
from worker import start_worker

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_event_handler("startup", start_worker)  # run worker


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tasks")
async def create_task() -> str:
    task = Task(id=str(uuid.uuid4()), status=TaskStatus.NEW, created_at=datetime.now(UTC))
    tasks[task.id] = task
    await queue.put(task.id)
    return task.id


@app.get("/tasks")
async def list_tasks() -> list[Task]:
    return list(tasks.values())


@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> Task:
    return tasks[task_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
