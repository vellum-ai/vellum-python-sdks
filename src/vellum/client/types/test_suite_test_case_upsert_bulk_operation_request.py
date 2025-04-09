# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value_request import ArrayVellumValueRequest
import pydantic
import typing
from .upsert_test_suite_test_case_request import UpsertTestSuiteTestCaseRequest
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class TestSuiteTestCaseUpsertBulkOperationRequest(UniversalBaseModel):
    """
    A bulk operation that represents the upserting of a Test Case.
    """

    id: str = pydantic.Field()
    """
    An ID representing this specific operation. Can later be used to look up information about the operation's success in the response.
    """

    type: typing.Literal["UPSERT"] = "UPSERT"
    data: UpsertTestSuiteTestCaseRequest

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
