import aiodocker
from starlette.requests import Request


def get_docker(request: Request) -> aiodocker.Docker:
    return request.app.state.docker  # type: ignore[no-any-return]
