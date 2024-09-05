# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .array_vellum_value_item_request import ArrayVellumValueItemRequest
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class NamedTestCaseArrayVariableValueRequest(UniversalBaseModel):
    """
    Named Test Case value that is of type ARRAY
    """

    type: typing.Literal["ARRAY"] = "ARRAY"
    value: typing.Optional[typing.List[ArrayVellumValueItemRequest]] = None
    name: str

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow