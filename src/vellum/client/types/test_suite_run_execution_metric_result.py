# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
from .test_suite_run_metric_output import TestSuiteRunMetricOutput
from .test_suite_run_execution_metric_definition import TestSuiteRunExecutionMetricDefinition
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class TestSuiteRunExecutionMetricResult(UniversalBaseModel):
    metric_id: str
    outputs: typing.List[TestSuiteRunMetricOutput]
    metric_label: typing.Optional[str] = None
    metric_definition: typing.Optional[TestSuiteRunExecutionMetricDefinition] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
