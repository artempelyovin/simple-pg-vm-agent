import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiodocker
import uvicorn
from fastapi import FastAPI

from models import InstallPostgresInputTaskData, InstallPostgresTask, StartPostgresTask, StopPostgresTask, Task
from settings import settings
from task_queue import queue, tasks
from worker import worker_loop

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    docker = aiodocker.Docker(url=settings.docker.url) if settings.docker.url else aiodocker.Docker()
    worker_task = asyncio.create_task(worker_loop(docker=docker))

    yield

    worker_task.cancel()
    await docker.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks")
async def list_tasks() -> list[Task]:
    return list(tasks.values())


@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> Task:
    return tasks[task_id]


@app.post("/install-postgres")
async def install_postgres(body: InstallPostgresInputTaskData) -> str:
    task = InstallPostgresTask(data=body)
    tasks[task.id] = task
    await queue.put(task.id)
    return task.id


@app.post("/start-postgres")
async def start_postgres() -> str:
    task = StartPostgresTask()
    tasks[task.id] = task
    await queue.put(task.id)
    return task.id


@app.post("/stop-postgres")
async def stop_postgres() -> str:
    task = StopPostgresTask()
    tasks[task.id] = task
    await queue.put(task.id)
    return task.id


if __name__ == "__main__":
    uvicorn.run(app, host=settings.app.host, port=settings.app.port)
