from dataclasses import dataclass
from .utils import (
    DevopnessClientAsync,
    ListArgs,
    ensure_authenticated,
    get_args_from_helper,
)


@dataclass
class ListEnvironments:
    project_id: int


async def list_environments(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, ListEnvironments)

    response = await devopness.environments.list_project_environments(parsed.project_id)

    environments = [
        {
            "id": environment.id,
            "name": environment.name,
            "type": environment.type,
            "description": environment.description,
        }
        for environment in response.data
    ]

    return {
        "data": environments,
        "count": len(environments),
    }
