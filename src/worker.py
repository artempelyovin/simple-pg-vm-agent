import asyncio
import logging
import traceback
from datetime import UTC, datetime

import aiodocker

from domain import postgres
from domain.enums import TaskStatus, TaskType
from domain.models import FlowContext, Task
from task_queue import queue, tasks

logger = logging.getLogger(__name__)

flow_by_task_type = {
    TaskType.INSTALL_POSTGRES: postgres.install_postgres,
    TaskType.START_POSTGRES: postgres.start_postgres,
    TaskType.STOP_POSTGRES: postgres.stop_postgres,
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
        ctx = FlowContext(data=task.data, docker=docker)
        result = await flow(ctx=ctx)  # type: ignore [operator]
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
