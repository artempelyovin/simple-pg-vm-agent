from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiodocker.containers import DockerContainer


class BasePostgresAgentError(Exception, ABC):
    @abstractmethod
    def message(self) -> str:
        pass


@dataclass(frozen=True)
class PostgresContainerNotFoundError(BasePostgresAgentError):
    def message(self) -> str:
        return "Container postgres not found"


@dataclass(frozen=True)
class MultiplePostgresContainersError(BasePostgresAgentError):
    containers: list[DockerContainer]

    def message(self) -> str:
        container_ids = ", ".join(c.id for c in self.containers)
        return f"Multiple postgres containers found: {container_ids}"
