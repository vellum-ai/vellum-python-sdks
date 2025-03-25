# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .test_suite_test_case_created_bulk_result_data import TestSuiteTestCaseCreatedBulkResultData
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class TestSuiteTestCaseCreatedBulkResult(UniversalBaseModel):
    """
    The result of a bulk operation that created a Test Case.
    """

    id: str
    type: typing.Literal["CREATED"] = "CREATED"
    data: TestSuiteTestCaseCreatedBulkResultData

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
