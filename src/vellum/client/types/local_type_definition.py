from typing import Any, Dict

from vellum.client.core.pydantic_utilities import UniversalBaseModel


class LocalTypeDefinition(UniversalBaseModel):
    id: str
    name: str
    schema: Dict[str, Any]
