from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DockerSettings(BaseModel):
    url: str | None = None


class Settings(BaseSettings):
    docker: DockerSettings

    model_config = SettingsConfigDict(
        env_file="envs/local.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
