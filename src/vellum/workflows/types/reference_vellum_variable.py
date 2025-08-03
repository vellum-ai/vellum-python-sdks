import typing
from typing import Optional

from pydantic import BaseModel

from vellum.workflows.types.local_type_reference import LocalTypeReference


class ReferenceVellumVariable(BaseModel):
    id: str
    key: str = ""
    type: typing.Literal["REFERENCE"] = "REFERENCE"
    required: Optional[bool] = None
    reference: LocalTypeReference
