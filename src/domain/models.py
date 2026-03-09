from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import aiodocker

from domain.enums import TaskStatus, TaskType
from domain.utils import now_utc, uuid4_str


@dataclass
class Task:
    id: str = field(default_factory=uuid4_str)
    task_type: TaskType = None  # type: ignore[assignment]
    status: TaskStatus = TaskStatus.NEW
    data: Any = None
    result: Any | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=now_utc)
    started_at: datetime | None = None
    finished_at: datetime | None = None


@dataclass
class InstallPostgresTaskData:
    version: str
    port: int


@dataclass
class InstallPostgresTaskResult:
    container_id: str


class InstallPostgresTask(Task):
    task_type: TaskType = field(default=TaskType.INSTALL_POSTGRES)
    data: InstallPostgresTaskData
    result: InstallPostgresTaskResult


class StartPostgresTask(Task):
    task_type: TaskType = field(default=TaskType.START_POSTGRES)


class StopPostgresTask(Task):
    task_type: TaskType = field(default=TaskType.STOP_POSTGRES)


@dataclass
class FlowContext[TData = None]:
    data: TData
    docker: aiodocker.Docker
