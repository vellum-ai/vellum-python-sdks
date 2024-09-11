# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import datetime as dt
from .test_suite_run_test_suite import TestSuiteRunTestSuite
from .test_suite_run_state import TestSuiteRunState
import pydantic
import typing
from .test_suite_run_exec_config import TestSuiteRunExecConfig
from ..core.pydantic_utilities import IS_PYDANTIC_V2
from ..core.pydantic_utilities import update_forward_refs


class TestSuiteRunRead(UniversalBaseModel):
    id: str
    created: dt.datetime
    test_suite: TestSuiteRunTestSuite
    state: TestSuiteRunState = pydantic.Field()
    """
    The current state of this run
    
    - `QUEUED` - Queued
    - `RUNNING` - Running
    - `COMPLETE` - Complete
    - `FAILED` - Failed
    - `CANCELLED` - Cancelled
    """

    exec_config: typing.Optional[TestSuiteRunExecConfig] = pydantic.Field(default=None)
    """
    Configuration that defines how the Test Suite should be run
    """

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(ArrayVellumValue)
