from enum import StrEnum


class TaskStatus(StrEnum):
    NEW = "new"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(StrEnum):
    INSTALL_POSTGRES = "install_postgres"
    START_POSTGRES = "start_postgres"
    STOP_POSTGRES = "stop_postgres"


class PostgresStatus(StrEnum):
    OK = "ok"
    STARTING = "starting"
    FAILED = "failed"
    NOT_CREATED = "not_created"
