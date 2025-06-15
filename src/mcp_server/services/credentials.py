from dataclasses import dataclass
from .utils import (
    DevopnessClientAsync,
    ListArgs,
    ensure_authenticated,
    get_args_from_helper,
)


@dataclass
class ListCredentials:
    environment_id: int


async def list_credentials(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, ListCredentials)

    response = await devopness.credentials.list_environment_credentials(
        parsed.environment_id
    )

    return response.data
