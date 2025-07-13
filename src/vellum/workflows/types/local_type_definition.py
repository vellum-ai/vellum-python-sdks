from typing import Any, Dict

from pydantic import BaseModel


class LocalTypeDefinition(BaseModel):
    id: str
    name: str
    schema: Dict[str, Any]
