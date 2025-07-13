import typing
from typing import Optional

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.local_type_reference import LocalTypeReference
from vellum.client.types.vellum_variable_extensions import VellumVariableExtensions


class ReferenceVellumVariable(UniversalBaseModel):
    id: str
    key: str = ""
    type: typing.Literal["REFERENCE"] = "REFERENCE"
    required: Optional[bool] = None
    reference: LocalTypeReference
    extensions: Optional[VellumVariableExtensions] = None
