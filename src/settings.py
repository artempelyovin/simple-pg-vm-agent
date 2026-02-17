from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DockerSettings(BaseModel):
    url: str | None = None


class AppSettings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000


class Settings(BaseSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    docker: DockerSettings = Field(default_factory=DockerSettings)

    model_config = SettingsConfigDict(
        env_file="envs/local.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
