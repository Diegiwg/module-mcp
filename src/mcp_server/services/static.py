from dataclasses import dataclass
from .utils import (
    DevopnessClientAsync,
    ListArgs,
    ensure_authenticated,
    get_args_from_helper,
)

from devopness.models import ProviderCode, CloudProviderServiceCode, CloudOsVersionCode


@dataclass
class ListSupportedProviders:
    pass


async def list_supported_providers(devopness: DevopnessClientAsync, args: ListArgs):
    return {
        "providers": [el.value for el in ProviderCode],
        "provider_services": [el.value for el in CloudProviderServiceCode],
    }


@dataclass
class ListRegionsOfProviderService:
    provider_service: CloudProviderServiceCode


async def list_regions_of_provider_service(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, ListRegionsOfProviderService)

    response = await devopness.static.get_static_cloud_provider_service(
        parsed.provider_service
    )

    regions = [
        {
            "code": region.code,
            "name": region.name,
        }
        for region in (response.data.regions or [])
    ]

    return {
        "data": regions,
        "count": len(regions),
    }


@dataclass
class ListInstanceTypesOfProviderServiceRegion:
    provider_service: CloudProviderServiceCode
    region: str


async def list_instance_types_of_provider_service_region(
    devopness: DevopnessClientAsync, args: ListArgs
):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, ListInstanceTypesOfProviderServiceRegion)

    response = await devopness.static.list_static_cloud_instances_by_cloud_provider_service_code_and_region_code(
        parsed.provider_service, region_code=parsed.region
    )

    instance_types = [
        instance_type  # TODO: reduce amount of data
        for instance_type in response.data
    ]

    return {
        "data": instance_types,
        "count": len(instance_types),
    }


@dataclass
class ListSupportedOsVersions:
    ...


async def list_supported_os_versions(devopness: DevopnessClientAsync, args: ListArgs):
    list_os = [el.value for el in CloudOsVersionCode]
    
    return {
        "data": list_os,
        "count": len(list_os),
    }