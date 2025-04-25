import os
from typing import List, Optional

from vellum import Vellum, VellumEnvironment


def create_vellum_client(api_key: Optional[str] = None, api_url: Optional[str] = None) -> Vellum:
    if api_key is None:
        api_key = os.getenv("VELLUM_API_KEY", default="")

    return Vellum(
        api_key=api_key,
        environment=create_vellum_environment(api_url),
    )


def create_vellum_environment(api_url: Optional[str] = None) -> VellumEnvironment:
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
