# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value_request import ArrayVellumValueRequest
import typing
import pydantic
from .named_test_case_variable_value_request import NamedTestCaseVariableValueRequest
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class CreateTestSuiteTestCaseRequest(UniversalBaseModel):
    """
    Information about the Test Case to create
    """

    label: typing.Optional[str] = pydantic.Field(default=None)
    """
    A human-readable label used to convey the intention of this Test Case
    """

    input_values: typing.List[NamedTestCaseVariableValueRequest] = pydantic.Field()
    """
    Values for each of the Test Case's input variables
    """

    evaluation_values: typing.List[NamedTestCaseVariableValueRequest] = pydantic.Field()
    """
    Values for each of the Test Case's evaluation variables
    """

    external_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    Optionally provide an ID that uniquely identifies this Test Case in your system. Useful for updating this Test Cases data after initial creation. Cannot be changed later.
    """

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
