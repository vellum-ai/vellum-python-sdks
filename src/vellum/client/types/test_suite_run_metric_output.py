# This file was auto-generated by Fern from our API Definition.

import typing
from .test_suite_run_metric_string_output import TestSuiteRunMetricStringOutput
from .test_suite_run_metric_number_output import TestSuiteRunMetricNumberOutput
from .test_suite_run_metric_json_output import TestSuiteRunMetricJsonOutput
from .test_suite_run_metric_error_output import TestSuiteRunMetricErrorOutput
from .test_suite_run_metric_array_output import TestSuiteRunMetricArrayOutput

TestSuiteRunMetricOutput = typing.Union[
    TestSuiteRunMetricStringOutput,
    TestSuiteRunMetricNumberOutput,
    TestSuiteRunMetricJsonOutput,
    TestSuiteRunMetricErrorOutput,
    TestSuiteRunMetricArrayOutput,
]
