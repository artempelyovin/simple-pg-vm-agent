import datetime
import uuid

from aiodocker import Docker
from aiodocker.containers import DockerContainer

from domain.errors import MultiplePostgresContainersError, PostgresContainerNotFoundError


def uuid4_str() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


async def get_postgres_container(docker: Docker) -> DockerContainer:
    containers = await docker.containers.list(all=True, filters={"name": ["postgres"]})
    if len(containers) == 0:
        raise PostgresContainerNotFoundError
    if len(containers) > 1:
        container_ids = [c.id for c in containers]
        raise MultiplePostgresContainersError(container_ids=container_ids)
    return containers[0]
