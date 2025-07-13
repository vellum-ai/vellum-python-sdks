from vellum.client.core.pydantic_utilities import UniversalBaseModel


class LocalTypeReference(UniversalBaseModel):
    type_definition_id: str
