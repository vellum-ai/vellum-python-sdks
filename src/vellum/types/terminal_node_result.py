# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_variable_value import ArrayVariableValue
import typing
from .terminal_node_result_data import TerminalNodeResultData
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs


class TerminalNodeResult(UniversalBaseModel):
    """
    A Node Result Event emitted from a Terminal Node.
    """

    type: typing.Literal["TERMINAL"] = "TERMINAL"
    data: TerminalNodeResultData

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(ArrayVariableValue)
