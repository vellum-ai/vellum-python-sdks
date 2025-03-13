import os
from typing import Optional

from vellum import Vellum, VellumEnvironment


def create_vellum_client(api_key: Optional[str] = None) -> Vellum:
    if api_key is None:
        api_key = os.getenv("VELLUM_API_KEY", default="")

    return Vellum(
        api_key=api_key,
        environment=create_vellum_environment(),
    )


def create_vellum_environment() -> VellumEnvironment:
    return VellumEnvironment(
        default=os.getenv("VELLUM_DEFAULT_API_URL", os.getenv("VELLUM_API_URL", "https://api.vellum.ai")),
        documents=os.getenv("VELLUM_DOCUMENTS_API_URL", os.getenv("VELLUM_API_URL", "https://documents.vellum.ai")),
        predict=os.getenv("VELLUM_PREDICT_API_URL", os.getenv("VELLUM_API_URL", "https://predict.vellum.ai")),
    )
