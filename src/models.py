from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class CreateDB(BaseModel):
    version: str


class TaskStatus(StrEnum):
    NEW = "new"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(StrEnum):
    CREATE_DB = "create_db"


class Task(BaseModel):
    id: str
    task_type: TaskType
    status: TaskStatus
    data: BaseModel
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class CreateDBTask(Task):
    task_type: TaskType = TaskType.CREATE_DB
    data: CreateDB
