import os
from typing import TYPE_CHECKING, List, Optional

from vellum.client.types.api_version_enum import ApiVersionEnum

if TYPE_CHECKING:
    from vellum.client import Vellum
    from vellum.client.environment import VellumEnvironment


def create_vellum_client(
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    api_version: Optional[ApiVersionEnum] = None,
) -> "Vellum":
    from vellum.client import Vellum

    if api_key is None:
        api_key = os.getenv("VELLUM_API_KEY", default="")

    return Vellum(
        api_key=api_key,
        environment=create_vellum_environment(api_url),
        api_version=api_version,
    )


def create_vellum_environment(api_url: Optional[str] = None) -> "VellumEnvironment":
    from vellum.client.environment import VellumEnvironment

    return VellumEnvironment(
        default=_resolve_env([api_url, "VELLUM_DEFAULT_API_URL", "VELLUM_API_URL"], "https://api.vellum.ai"),
        documents=_resolve_env([api_url, "VELLUM_DOCUMENTS_API_URL", "VELLUM_API_URL"], "https://documents.vellum.ai"),
        predict=_resolve_env([api_url, "VELLUM_PREDICT_API_URL", "VELLUM_API_URL"], "https://predict.vellum.ai"),
    )


def _resolve_env(names: List[Optional[str]], default: str = "") -> str:
    for name in names:
        if not name:
            continue

        value = os.getenv(name)
        if value:
            return value

    return default
