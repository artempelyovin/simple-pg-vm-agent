import asyncio

from models import Task

tasks: dict[str, Task] = {}
queue: asyncio.Queue[str] = asyncio.Queue()
