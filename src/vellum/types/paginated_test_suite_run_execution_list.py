# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
from .test_suite_run_execution import TestSuiteRunExecution
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs


class PaginatedTestSuiteRunExecutionList(UniversalBaseModel):
    count: int
    next: typing.Optional[str] = None
    previous: typing.Optional[str] = None
    results: typing.List[TestSuiteRunExecution]

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(ArrayVellumValue, PaginatedTestSuiteRunExecutionList=PaginatedTestSuiteRunExecutionList)
