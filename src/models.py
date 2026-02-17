from datetime import datetime
from enum import StrEnum

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


class Task[D, R](BaseModel):
    id: str
    task_type: TaskType
    status: TaskStatus
    data: D
    result: R | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
