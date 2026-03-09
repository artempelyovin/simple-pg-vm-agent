from typing import Annotated

from aiodocker import Docker
from fastapi import APIRouter, Depends

from api.dependencies import get_docker
from api.schemas import CheckResponseResponse, HealthResponse, InstallPostgresInput, TaskResponse
from domain.models import InstallPostgresTask, InstallPostgresTaskData, StartPostgresTask, StopPostgresTask
from domain.postgres import check_postgres_status
from task_queue import queue, tasks

router = APIRouter()


@router.get("/health", tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse.model_validate({"status": "ok"})


@router.get("/tasks", tags=["tasks"])
async def list_tasks() -> list[TaskResponse]:
    return [TaskResponse.model_validate(task, from_attributes=True) for task in tasks.values()]


@router.get("/tasks/{task_id}", tags=["tasks"])
async def get_task(task_id: str) -> TaskResponse:
    return TaskResponse.model_validate(tasks[task_id], from_attributes=True)


@router.post("/postgres/install", tags=["postgres"])
async def install_postgres(body: InstallPostgresInput) -> str:
    task = InstallPostgresTask(data=InstallPostgresTaskData(version=body.version, port=body.port))
    tasks[task.id] = task
    await queue.put(task.id)
    return task.id


@router.post("/postgres/check", tags=["postgres"])
async def check_postgres(docker: Annotated[Docker, Depends(get_docker)]) -> CheckResponseResponse:
    status = await check_postgres_status(docker=docker)
    return CheckResponseResponse.model_validate({"status": status})


@router.post("/postgres/start", tags=["postgres"])
async def start_postgres() -> str:
    task = StartPostgresTask()
    tasks[task.id] = task
    await queue.put(task.id)
    return task.id


@router.post("/postgres/stop", tags=["postgres"])
async def stop_postgres() -> str:
    task = StopPostgresTask()
    tasks[task.id] = task
    await queue.put(task.id)
    return task.id
