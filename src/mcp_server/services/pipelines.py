from dataclasses import dataclass
from .utils import (
    DevopnessClientAsync,
    ListArgs,
    ensure_authenticated,
    EnvironmentResourceType,
    get_args_from_helper,
)


@dataclass
class ListPipelines:
    resource_id: int
    resource_type: EnvironmentResourceType


async def list_pipelines(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, ListPipelines)

    response = await devopness.pipelines.list_pipelines_by_resource_type(
        parsed.resource_id, parsed.resource_type
    )

    pipelines = [
        {
            "id": pipeline.id,
            "name": pipeline.name,
            "operation": pipeline.operation_human_readable,
            "max_parallel_actions": pipeline.max_parallel_actions,
            "resource": {
                "id": pipeline.resource_id,
                "type": pipeline.resource_type_human_readable,
            },
        }
        for pipeline in response.data
    ]

    return {
        "data": pipelines,
        "count": len(pipelines),
    }
