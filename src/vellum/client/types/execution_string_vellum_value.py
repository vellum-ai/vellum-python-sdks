# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import pydantic
import typing
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class ExecutionStringVellumValue(UniversalBaseModel):
    """
    A value representing a string.
    """

    id: str = pydantic.Field()
    """
    The variable's uniquely identifying internal id.
    """

    name: str
    type: typing.Literal["STRING"] = "STRING"
    value: typing.Optional[str] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow