import asyncio
import logging
import traceback
from datetime import UTC, datetime
from typing import cast

import aiodocker
from aiodocker import Docker

from errors import PostgresContainerNotFoundError
from models import (
    FlowContext,
    InstallPostgresInputTaskData,
    InstallPostgresOutputTaskData,
    PostgresStatus,
    Task,
    TaskStatus,
    TaskType,
)
from task_queue import queue, tasks
from utils import get_postgres_container

logger = logging.getLogger(__name__)


async def install_postgres(ctx: FlowContext) -> InstallPostgresOutputTaskData:
    ctx.task.data = cast(InstallPostgresInputTaskData, ctx.task.data)  # noqa: TC006

    image = f"postgres:{ctx.task.data.version}"
    logger.info(f"Pull {image}")
    await ctx.docker.images.pull(from_image=image)
    logger.info(f"Create postgres container with image {image}")
    container = await ctx.docker.containers.create(
        config={
            "Image": image,
            "PortBinding": {
                "5432/tcp": [{"HostPort": ctx.task.data.port}],
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
    logger.info(f"Start postgres container {container['id']}")
    await container.start()
    return InstallPostgresOutputTaskData(container_id=container["id"])


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


async def start_postgres(ctx: FlowContext) -> None:
    container = await get_postgres_container(docker=ctx.docker)
    logger.info(f"Start postgres container {container.id}")
    await container.start()


async def stop_postgres(ctx: FlowContext) -> None:
    container = await get_postgres_container(docker=ctx.docker)
    logger.info(f"Stop postgres container {container.id}")
    await container.stop()


flow_by_task_type = {
    TaskType.INSTALL_POSTGRES: install_postgres,
    TaskType.START_POSTGRES: start_postgres,
    TaskType.STOP_POSTGRES: stop_postgres,
}


async def process_task(task: Task, docker: aiodocker.Docker) -> None:
    flow = flow_by_task_type.get(task.task_type)
    if flow is None:
        logger.warning(f"Flow for the {task.id} ({task.task_type}) task is not defined")
        return
    task.status = TaskStatus.RUNNING
    task.started_at = datetime.now(UTC)
    try:
        logger.info(f"Run {task.id} ({task.task_type}) task")
        ctx = FlowContext(task=task, docker=docker)
        result = await flow(ctx=ctx)
        task.result = result
        task.status = TaskStatus.COMPLETED
    except Exception:
        logger.exception(f"Task {task.id} ({task.task_type}) failed")
        task.status = TaskStatus.FAILED
        task.error = traceback.format_exc()
    finally:
        task.finished_at = datetime.now(UTC)


async def worker_loop(docker: aiodocker.Docker) -> None:
    logger.info("Worker started")
    while True:
        task_id = await queue.get()
        logger.info(f"Received {task_id} task")
        task = tasks.get(task_id)
        if task is None:
            logger.warning(f"Task {task_id} not found in storage")
            continue
        asyncio.create_task(process_task(task=task, docker=docker))  # noqa: RUF006
