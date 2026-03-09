import logging

from aiodocker import Docker

from domain.enums import PostgresStatus
from domain.errors import PostgresContainerNotFoundError
from domain.models import FlowContext, InstallPostgresTaskData, InstallPostgresTaskResult
from domain.utils import get_postgres_container

logger = logging.getLogger(__name__)


async def check_postgres_status(docker: Docker) -> PostgresStatus:
    logger.info("Check postgres container status")
    try:
        container = await get_postgres_container(docker=docker)
        container_info = await container.show()
    except PostgresContainerNotFoundError:
        return PostgresStatus.NOT_CREATED
    state = container_info["State"]
    status = state["Status"]
    health = state.get("Health", {}).get("Status")
    match (status, health):
        case ("running", "healthy") | ("running", None):
            return PostgresStatus.OK
        case ("running", "starting") | ("created", _) | ("restarting", _):
            return PostgresStatus.STARTING
        case ("running", "unhealthy") | ("exited", _) | ("dead", _):
            return PostgresStatus.FAILED
        case _:
            return PostgresStatus.FAILED


async def install_postgres(ctx: FlowContext[InstallPostgresTaskData]) -> InstallPostgresTaskResult:
    image = f"postgres:{ctx.data.version}"
    logger.info(f"Pull {image}")
    await ctx.docker.images.pull(from_image=image)
    logger.info(f"Create postgres container with image {image}")
    container = await ctx.docker.containers.create(
        config={
            "Image": image,
            "PortBinding": {
                "5432/tcp": [{"HostPort": ctx.data.port}],
            },
            "Env": ["POSTGRES_PASSWORD=secret"],  # TODO: generate password
            "Healthcheck": {
                "Test": ["CMD-SHELL", "pg_isready -U postgres"],
                "Interval": 10_000_000_000,  # 10 sec
                "Timeout": 5_000_000_000,  # 5 sec
                "Retries": 3,
            },
        },
        name="postgres",
    )
    logger.info(f"Start postgres container {container.id}")
    await container.start()
    return InstallPostgresTaskResult(container_id=container.id)


async def start_postgres(ctx: FlowContext) -> None:
    container = await get_postgres_container(docker=ctx.docker)
    logger.info(f"Start postgres container {container.id}")
    await container.start()


async def stop_postgres(ctx: FlowContext) -> None:
    container = await get_postgres_container(docker=ctx.docker)
    logger.info(f"Stop postgres container {container.id}")
    await container.stop()
