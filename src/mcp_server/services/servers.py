from dataclasses import dataclass
from .utils import (
    DevopnessClientAsync,
    ListArgs,
    ensure_authenticated,
    get_args_from_helper,
)


from devopness.models import ServerCloudServiceCode, CloudOsVersionCode


@dataclass
class ListServers:
    environment_id: int


async def list_servers(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, ListServers)

    response = await devopness.servers.list_environment_servers(parsed.environment_id)

    servers = [
        {
            "id": server.id,
            "name": server.hostname,
            "status": server.status,
            "ip_address": server.ip_address,
            "ssh_port": server.ssh_port,
            "last_action": (
                {
                    "id": server.last_action.id,
                    "type": server.last_action.type_human_readable,
                    "status": server.last_action.status_human_readable,
                    "url": server.last_action.url_web_permalink,
                }
                if server.last_action
                else None
            ),
            "provider": (
                {
                    "name": server.credential.provider.code_human_readable,
                    "region": server.region or "Unknown",
                    "credential": {
                        "id": server.credential.id,
                        "name": server.credential.name,
                    },
                }
                if server.credential
                else None
            ),
        }
        for server in response.data
    ]

    return {
        "data": servers,
        "count": len(servers),
    }


@dataclass
class CreateServer:
    environment_id: int
    credential_id: int
    cloud_service_code: ServerCloudServiceCode
    cloud_service_region: str
    cloud_service_instance_type: str
    os_hostname: str
    os_disk_size: int
    os_version_code: CloudOsVersionCode = CloudOsVersionCode.UBUNTU_24_04


async def devopness_create_server(
    devopness: DevopnessClientAsync,
    args: ListArgs,
):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, CreateServer)

    response = await devopness.servers.add_environment_server(
        parsed.environment_id,
        {
            "hostname": parsed.os_hostname,
            # TODO: credential_id type as INT on API Docs/SDK
            "credential_id": str(parsed.credential_id),
            "provision_input": {
                "cloud_service_code": parsed.cloud_service_code,
                # TODO: support server provision with custom subnet
                "settings": {
                    "region": parsed.cloud_service_region,
                    "instance_type": parsed.cloud_service_instance_type,
                    "os_version_code": parsed.os_version_code,
                    "storage_size": parsed.os_disk_size,
                },
            },
        },
    )

    return response.data
