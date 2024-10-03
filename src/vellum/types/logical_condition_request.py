# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .logical_operator import LogicalOperator
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class LogicalConditionRequest(UniversalBaseModel):
    """
    A basic condition comparing a two variables.
    """

    type: typing.Literal["LOGICAL_CONDITION"] = "LOGICAL_CONDITION"
    lhs_variable_id: str
    operator: LogicalOperator
    rhs_variable_id: str

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
