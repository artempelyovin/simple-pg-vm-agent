import asyncio
import logging
import traceback
from datetime import UTC, datetime

import aiodocker

from models import CreateDBInputTaskData, CreateDBOutputTaskData, Task, TaskStatus, TaskType
from task_queue import queue, tasks

logger = logging.getLogger(__name__)


async def create_db(data: CreateDBInputTaskData, docker_client: aiodocker.Docker) -> CreateDBOutputTaskData:
    logger.info(f"Pull postgres:{data.version}")
    image = await docker_client.images.pull(from_image=f"postgres:{data.version}")
    logger.info(f"Run container database with image {image.name}")
    container = await asyncio.to_thread(
        docker_client.containers.run,
        image=image.id,
        name="database",
        detach=True,
    )
    return CreateDBOutputTaskData(image_id=image.id, container_id=container.id)


flow_by_task_type = {
    TaskType.CREATE_DB: create_db,
}


async def process_task(task: Task, docker_client: aiodocker.Docker) -> None:
    flow = flow_by_task_type.get(task.task_type)
    if flow is None:
        logger.warning(f"Flow for the {task.id} ({task.task_type}) task is not defined")
        return
    task.status = TaskStatus.RUNNING
    task.started_at = datetime.now(UTC)
    try:
        logger.info(f"Run {task.id} ({task.task_type}) task")
        result = await flow(data=task.data, docker_client=docker_client)
        task.result = result
        task.status = TaskStatus.COMPLETED
    except Exception:
        logger.exception(f"Task {task.id} ({task.task_type}) failed")
        task.status = TaskStatus.FAILED
        task.error = traceback.format_exc()
    finally:
        task.finished_at = datetime.now(UTC)


async def worker_loop(docker_client: aiodocker.Docker) -> None:
    logger.info("Worker started")
    while True:
        task_id = await queue.get()
        logger.info(f"Received {task_id} task")
        task = tasks.get(task_id)
        if task is None:
            logger.warning(f"Task {task_id} not found in storage")
            continue
        asyncio.create_task(process_task(task=task, docker_client=docker_client))  # noqa: RUF006
