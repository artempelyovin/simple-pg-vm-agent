import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from domain.enums import PostgresStatus, TaskStatus, TaskType


class TaskResponse(BaseModel):
    id: uuid.UUID
    task_type: TaskType
    status: TaskStatus
    data: dict[str, Any] | None
    result: dict[str, Any] | None
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class HealthResponse(BaseModel):
    status: str = "ok"


class CheckResponseResponse(BaseModel):
    status: PostgresStatus


class InstallPostgresInput(BaseModel):
    version: str
    port: int = Field(5432, ge=1024, le=49151)


class InstallPostgresResponse(BaseModel):
    container_id: str
