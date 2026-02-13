import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, UTC
import uvicorn
import aiodocker
from fastapi import FastAPI
from models import Task, TaskStatus, TaskType, CreateDBInputTaskData
from settings import settings
from task_queue import tasks, queue
from worker import worker_loop

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.docker.url:
        docker_client = aiodocker.Docker(url=settings.docker.url)
    else:
        docker_client = aiodocker.Docker()
    app.state.docker = docker_client

    worker_task = asyncio.create_task(worker_loop(docker_client=docker_client))

    yield
    worker_task.cancel()
    await docker_client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/tasks")
async def list_tasks() -> list[Task]:
    return list(tasks.values())


@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> Task:
    return tasks[task_id]


@app.post("/create-db")
async def create_db(body: CreateDBInputTaskData) -> str:
    task = Task(
        id=str(uuid.uuid4()),
        task_type=TaskType.CREATE_DB,
        data=body,
        status=TaskStatus.NEW,
        created_at=datetime.now(UTC),
    )
    tasks[task.id] = task
    await queue.put(task.id)
    return task.id


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
