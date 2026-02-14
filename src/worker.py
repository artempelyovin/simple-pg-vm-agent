from typing import Any

import docker
from docker.errors import APIError as DockerAPIError
import asyncio
import logging
import traceback
from datetime import datetime, UTC

from models import TaskType, TaskStatus, Task, CreateDBInputTaskData, CreateDBOutputTaskData
from task_queue import queue, tasks

logger = logging.getLogger(__name__)


async def create_db(data: CreateDBInputTaskData) -> CreateDBOutputTaskData:
    client = docker.from_env()
    image = await asyncio.to_thread(client.images.get, f"postgres:{data.version}")
    if not image:
        logger.info(f"Pull postgres:{data.version}")
        image = await asyncio.to_thread(client.images.pull, repository="postgres", tag=data.version)
    logger.info(f"Run container database with image {image.name}")
    container = await asyncio.to_thread(
        client.containers.run,
        image=image.id,
        name="database",
        detach=True,
    )
    return CreateDBOutputTaskData(image_id=image.id, container_id=container.id)


flow_by_task_type = {
    TaskType.CREATE_DB: create_db,
}


def start_worker():
    asyncio.create_task(worker_loop())


async def worker_loop():
    logger.info("Worker started")
    while True:
        task_id = await queue.get()
        if task_id is None:
            continue

        logger.info(f"Received {task_id} task")
        task = tasks.get(task_id)
        if task is None:
            logger.warning(f"Task {task_id} not found in storage")
        flow = flow_by_task_type.get(task.task_type)
        if flow is None:
            logger.warning(f"Flow for the {task.id} ({task.task_type}) task is not defined")
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(UTC)
        try:
            logger.info(f"Run {task.id} ({task.task_type}) task")
            result = await flow(task.data)
            task.reason = result
            task.status = TaskStatus.COMPLETED
        except Exception:
            logger.exception(f"Task {task_id} ({task.task_type}) failed")
            task.status = TaskStatus.FAILED
            task.error = traceback.format_exc()
        finally:
            task.finished_at = datetime.now(UTC)
