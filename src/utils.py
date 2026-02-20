from aiodocker import Docker
from aiodocker.containers import DockerContainer

from errors import MultiplePostgresContainersError, PostgresContainerNotFoundError


async def get_postgres_container(docker: Docker) -> DockerContainer:
    containers = await docker.containers.list(all=True, filters={"name": ["postgres"]})
    if len(containers) == 0:
        raise PostgresContainerNotFoundError
    if len(containers) > 1:
        container_ids = [c.id for c in containers]
        raise MultiplePostgresContainersError(container_ids=container_ids)
    return containers[0]
