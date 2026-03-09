import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiodocker
import uvicorn
from fastapi import FastAPI

from api.routes import router
from settings import settings
from worker import worker_loop

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    docker = aiodocker.Docker(url=settings.docker_url) if settings.docker_url else aiodocker.Docker()
    worker_task = asyncio.create_task(worker_loop(docker=docker))
    _app.state.docker = docker

    yield

    worker_task.cancel()
    await docker.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
