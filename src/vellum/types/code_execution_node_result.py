# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .code_execution_node_result_data import CodeExecutionNodeResultData
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs
from .array_variable_value import ArrayVariableValue


class CodeExecutionNodeResult(UniversalBaseModel):
    """
    A Node Result Event emitted from a Code Execution Node.
    """

    type: typing.Literal["CODE_EXECUTION"] = "CODE_EXECUTION"
    data: CodeExecutionNodeResultData

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(ArrayVariableValue)
