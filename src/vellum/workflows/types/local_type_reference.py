from pydantic import BaseModel


class LocalTypeReference(BaseModel):
    type_definition_id: str
