import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

import aiodocker
from pydantic import BaseModel, Field


class InstallPostgresInputTaskData(BaseModel):
    version: str
    port: int = Field(5432, ge=1024, le=49151)


class InstallPostgresOutputTaskData(BaseModel):
    container_id: str


class TaskStatus(StrEnum):
    NEW = "new"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(StrEnum):
    INSTALL_POSTGRES = "install_postgres"
    START_POSTGRES = "start_postgres"
    STOP_POSTGRES = "stop_postgres"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType
    status: TaskStatus = TaskStatus.NEW
    data: BaseModel | None = None
    result: BaseModel | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda _: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None


class InstallPostgresTask(Task):
    data: InstallPostgresInputTaskData
    task_type: TaskType = TaskType.INSTALL_POSTGRES


class StartPostgresTask(Task):
    task_type: TaskType = TaskType.START_POSTGRES


class StopPostgresTask(Task):
    task_type: TaskType = TaskType.STOP_POSTGRES


@dataclass
class FlowContext:
    task: Task
    docker: aiodocker.Docker
