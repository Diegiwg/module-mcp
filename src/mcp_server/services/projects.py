from dataclasses import dataclass
from .utils import DevopnessClientAsync, ListArgs, ensure_authenticated


@dataclass
class ListProjects: ...


async def list_projects(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    response = await devopness.projects.list_projects()

    projects = [
        {
            "id": project.id,
            "name": project.name,
        }
        for project in response.data
    ]

    return {
        "data": projects,
        "count": len(projects),
    }
