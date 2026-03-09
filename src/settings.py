import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    docker_url: str | None
    api_host: str
    api_port: int


settings = Settings(
    docker_url=os.getenv("DOCKER_URL"),
    api_host=os.getenv("API_HOST", "127.0.0.1"),
    api_port=int(os.getenv("API_PORT", "8000")),
)
