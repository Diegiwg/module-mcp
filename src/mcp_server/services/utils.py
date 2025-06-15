from dataclasses import fields, is_dataclass
from enum import Enum
import os
from typing import (
    Any,
    Dict,
    Literal,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from devopness import DevopnessClientAsync

Operations = Literal[
    "__help__",
    "list_projects",
    "list_environments",
    "list_servers",
    "list_applications",
    "list_pipelines",
    "list_supported_providers",
    "list_regions_of_provider_service",
    "list_instance_types_of_provider_service_region",
    "deploy_application",
    "create_server",
    "list_credentials",
    "list_supported_os_versions",
]


ListArgs = Dict[str, Any] | None
ArgType = TypeVar("ArgType")


class EnvironmentResourceType(str, Enum):
    SERVER = "server"
    APPLICATION = "application"

    def __str__(self):
        return self.value


def get_arg(arg_name: str, arg_type: Type[ArgType], args: ListArgs) -> ArgType:
    if args is None:
        raise ValueError(
            f"Missing argument: '{arg_name}' with type '{arg_type.__name__}'"
        )

    if arg_name not in args:
        raise ValueError(
            f"Missing argument: '{arg_name}' with type '{arg_type.__name__}'"
        )

    value = args[arg_name]

    if isinstance(arg_type, type) and issubclass(arg_type, Enum):
        try:
            return arg_type(value)  # type: ignore
        except ValueError:
            raise ValueError(f"Invalid value for argument '{arg_name}': '{value}'")

    if not isinstance(value, arg_type):
        raise TypeError(
            f"Argument '{arg_name}' must be of type '{arg_type.__name__}', got '{type(value).__name__}'"
        )

    return value


def get_optional_arg(
    arg_name: str,
    arg_type: Type[ArgType],
    args: ListArgs,
) -> ArgType | None:
    if args is None or arg_name not in args:
        return None

    return get_arg(arg_name, arg_type, args)


def get_args_from_helper(
    args: ListArgs,
    args_model: type[ArgType],
) -> ArgType:
    if not is_dataclass(args_model):
        raise TypeError("args_model must be a dataclass")

    kwargs = {}

    for field in fields(args_model):
        arg_name = field.name
        arg_type = field.type

        origin = get_origin(arg_type)

        if origin is Union:
            inner_types = get_args(arg_type)
            non_none = [t for t in inner_types if t is not type(None)]
            if len(non_none) == 1:
                actual_type = non_none[0]
                if not isinstance(actual_type, type):
                    raise TypeError(
                        f"Invalid optional inner type for '{arg_name}': {actual_type}"
                    )
                kwargs[arg_name] = get_optional_arg(arg_name, actual_type, args)
                continue

        if not isinstance(arg_type, type):
            raise TypeError(
                f"Invalid type for field '{arg_name}': {arg_type} (expected real Python type)"
            )

        kwargs[arg_name] = get_arg(arg_name, arg_type, args)

    return args_model(**kwargs)


def get_helper(
    operation: str,
    args_model: type,
) -> str:
    if not is_dataclass(args_model):
        raise TypeError("args_model must be a dataclass")

    msg = f"To perform the '{operation}' operation, you must specify the following arguments:"

    for field in fields(args_model):
        arg_name = field.name
        arg_type = field.type

        origin = get_origin(arg_type)

        if origin is Union:
            inner_types = get_args(arg_type)
            non_none = [t for t in inner_types if t is not type(None)]
            if len(non_none) == 1:
                arg_type = non_none[0]
                optional_suffix = " (optional)"
            else:
                optional_suffix = ""
        else:
            optional_suffix = ""

        type_name = getattr(arg_type, "__name__", str(arg_type))

        msg += f"\n- {arg_name}: {type_name}{optional_suffix}"

    return msg


async def ensure_authenticated(devopness: DevopnessClientAsync) -> None:
    user_email = os.environ.get("DEVOPNESS_USER_EMAIL")
    user_pass = os.environ.get("DEVOPNESS_USER_PASSWORD")

    if not user_email or not user_pass:
        raise Exception("DEVOPNESS_USER_EMAIL and DEVOPNESS_USER_PASSWORD must be set")

    await devopness.users.login_user(
        {
            "email": user_email,
            "password": user_pass,
        }
    )
