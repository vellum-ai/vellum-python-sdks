from typing import Any, Dict

from pydantic import BaseModel


class LocalTypeDefinition(BaseModel):
    id: str
    name: str
    type_schema: Dict[str, Any]
