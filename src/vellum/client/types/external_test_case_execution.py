# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
from .named_test_case_variable_value import NamedTestCaseVariableValue
import pydantic
from ..core.pydantic_utilities import IS_PYDANTIC_V2
from ..core.pydantic_utilities import update_forward_refs


class ExternalTestCaseExecution(UniversalBaseModel):
    outputs: typing.List[NamedTestCaseVariableValue] = pydantic.Field()
    """
    The output values of a callable that was executed against a Test Case outside of Vellum
    """

    test_case_id: str

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(ArrayVellumValue, ExternalTestCaseExecution=ExternalTestCaseExecution)
