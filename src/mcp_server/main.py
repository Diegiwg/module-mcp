import logging
from typing import Any

from devopness import DevopnessClientAsync
from fastmcp import FastMCP

from .services.static import (
    ListInstanceTypesOfProviderServiceRegion,
    ListRegionsOfProviderService,
    ListSupportedProviders,
    list_instance_types_of_provider_service_region,
    list_regions_of_provider_service,
    list_supported_providers,
)

from .services.applications import (
    DeployApplication,
    ListApplications,
    deploy_application,
    list_applications,
)
from .services.environments import (
    ListEnvironments,
    list_environments,
)
from .services.pipelines import (
    ListPipelines,
    list_pipelines,
)
from .services.projects import (
    ListProjects,
    list_projects,
)
from .services.servers import (
    CreateServer,
    DeleteServer,
    ListServers,
    StopServer,
    delete_server,
    devopness_create_server,
    list_servers,
    stop_server,
)
from .services.static import list_supported_os_versions, ListSupportedOsVersions
from .services.credentials import list_credentials, ListCredentials
from .services.utils import Operations, get_helper

server: FastMCP = FastMCP()

devopness = DevopnessClientAsync(
    {
        "base_url": "https://api.devopness.com",
        "debug": True,
    }
)

logger = logging.getLogger()


def operation_helper(args: dict[str, Any] | None) -> str:
    if args is None:
        args = {}

    if "operation" not in args:
        msg = "Please specify an operation in args {'operation': <operation_name>}.\n"

        msg += "Available operations:\n"
        msg += Operations.__str__()

        return msg

    operation: Operations = args["operation"]
    match operation:
        case "deploy_application":
            return get_helper(operation, DeployApplication)

        case "list_applications":
            return get_helper(operation, ListApplications)

        case "list_projects":
            return get_helper(operation, ListProjects)

        case "list_environments":
            return get_helper(operation, ListEnvironments)

        case "list_servers":
            return get_helper(operation, ListServers)

        case "list_pipelines":
            return get_helper(operation, ListPipelines)

        case "create_server":
            return get_helper(operation, CreateServer)

        case "list_supported_providers":
            return get_helper(operation, ListSupportedProviders)

        case "list_regions_of_provider_service":
            return get_helper(operation, ListRegionsOfProviderService)

        case "list_instance_types_of_provider_service_region":
            return get_helper(operation, ListInstanceTypesOfProviderServiceRegion)

        case "list_credentials":
            return get_helper(operation, ListCredentials)

        case "list_supported_os_versions":
            return get_helper(operation, ListSupportedOsVersions)

        case "stop_server":
            return get_helper(operation, StopServer)

        case "delete_server":
            return get_helper(operation, DeleteServer)

        case _:
            return f"Unknown operation: {args['operation']}"


@server.tool()
async def devopness_perform_any_operation(
    operation: Operations,
    args: dict[str, Any] | None = None,
) -> Any:
    """
    Perform any operation using Devopness API.

    Rules:
    1. Before performing any operation, you must execute the `__help__` operation,
       with the operation you want to perform as an argument, to get the list
       of arguments for that operation.
       - Example: `devopness_perform_any_operation('deploy_application')`
    """
    match operation:
        case "__help__":
            return operation_helper(args)

        case "list_projects":
            return await list_projects(devopness, args)

        case "list_environments":
            return await list_environments(devopness, args)

        case "list_servers":
            return await list_servers(devopness, args)

        case "list_applications":
            return await list_applications(devopness, args)

        case "list_pipelines":
            return await list_pipelines(devopness, args)

        case "deploy_application":
            return await deploy_application(devopness, args)

        case "create_server":
            return await devopness_create_server(devopness, args)

        case "list_supported_providers":
            return await list_supported_providers(devopness, args)

        case "list_regions_of_provider_service":
            return await list_regions_of_provider_service(devopness, args)

        case "list_instance_types_of_provider_service_region":
            return await list_instance_types_of_provider_service_region(devopness, args)

        case "list_credentials":
            return await list_credentials(devopness, args)

        case "list_supported_os_versions":
            return await list_supported_os_versions(devopness, args)

        case "stop_server":
            return await stop_server(devopness, args)

        case "delete_server":
            return await delete_server(devopness, args)

        case _:
            return f"Unknown operation: {operation}"


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
