from dataclasses import dataclass


class BasePostgresAgentError(Exception):
    pass


class PostgresContainerNotFoundError(BasePostgresAgentError):
    def __str__(self) -> str:
        return "Container postgres not found"


@dataclass(frozen=True)
class MultiplePostgresContainersError(BasePostgresAgentError):
    container_ids: list[str]

    def __str__(self) -> str:
        container_ids = ", ".join(self.container_ids)
        return f"Multiple postgres containers found: {container_ids}"
