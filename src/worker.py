import asyncio
import logging

from models import CreateDBTask, TaskType
from task_queue import queue, tasks

logger = logging.getLogger(__name__)


async def create_db(task: CreateDBTask) -> None:
    logger.info(f"Run {task.id} task ({task.task_type})")


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
            raise RuntimeError(f"Task {task_id} not found in storage")
        flow = flow_by_task_type.get(task.task_type)
        if flow is None:
            raise RuntimeError(f"Flow for the {task.task_type} task type is not defined")
        await flow(task)
