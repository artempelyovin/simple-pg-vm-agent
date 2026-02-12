import asyncio
import logging

from task_queue import queue

logger = logging.getLogger(__name__)


async def worker_loop():
    logger.info("Worker started")
    while True:
        task_id = await queue.get()
        logger.info(f"Worker {task_id} starting")


def start_worker():
    asyncio.create_task(worker_loop())
