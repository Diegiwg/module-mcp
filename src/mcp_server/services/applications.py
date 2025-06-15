from dataclasses import dataclass
from typing import Optional

from devopness.models import (
    ActionPipelineCreatePlain,
    ApplicationEnvironmentCreatePlain,
    SourceType,
)

from .utils import (
    DevopnessClientAsync,
    ListArgs,
    ensure_authenticated,
    get_args_from_helper,
)


@dataclass
class ListApplications:
    environment_id: int


async def list_applications(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, ListApplications)

    response = await devopness.applications.list_environment_applications(
        parsed.environment_id
    )

    applications = [
        {
            "id": application.id,
            "name": application.name,
            "repository_url": application.repository,
            "stack": {
                "language": application.programming_language_human_readable,
                "version": application.engine_version,
                "framework": application.framework_human_readable,
            },
            # "last_deployments": application.last_deployments,
            "credential": (
                {
                    "id": application.credential.id,
                    "name": application.credential.name,
                    "provider": application.credential.provider.code_human_readable,
                }
                if application.credential
                else None
            ),
        }
        for application in response.data
    ]

    return {
        "data": applications,
        "count": len(applications),
    }


@dataclass
class DeployApplication:
    deploy_pipeline_id: int
    deploy_source_type: SourceType
    deploy_source_value: str
    server_ids_to_deploy: Optional[list[int]] = None


async def deploy_application(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, DeployApplication)

    deploy_config: ActionPipelineCreatePlain = {
        "source_type": parsed.deploy_source_type,
        "source_ref": parsed.deploy_source_value,
    }

    if parsed.server_ids_to_deploy:
        deploy_config["servers"] = parsed.server_ids_to_deploy

    response = await devopness.actions.add_pipeline_action(
        parsed.deploy_pipeline_id,
        deploy_config,
    )

    return response.data


@dataclass
class CreateApplication:
    environment_id: int
    application_name: str
    repository_credential_id: int
    repository_owner_and_name: str
    repository_default_branch: str
    programming_language: str
    programming_language_version: str
    programming_language_framework: str = "none"
    repository_working_directory: Optional[str] = None


async def create_application(devopness: DevopnessClientAsync, args: ListArgs):
    await ensure_authenticated(devopness)

    parsed = get_args_from_helper(args, CreateApplication)

    data: ApplicationEnvironmentCreatePlain = {
        "name": parsed.application_name,
        "repository": parsed.repository_owner_and_name,
        "programming_language": parsed.programming_language,
        "engine_version": parsed.programming_language_version,
        "framework": parsed.programming_language_framework,
        "root_directory": parsed.repository_working_directory,
        "default_branch": parsed.repository_default_branch,
        "credential_id": parsed.repository_credential_id,
    }

    response = await devopness.applications.add_environment_application(
        parsed.environment_id, data
    )

    return response.data
