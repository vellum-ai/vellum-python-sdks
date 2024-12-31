from __future__ import annotations

from functools import cached_property
import logging
import time
from uuid import UUID
from typing import Callable, Generator, Iterable, List, cast

from vellum import TestSuiteRunMetricNumberOutput, TestSuiteRunRead
from vellum.client import OMIT, Vellum
from vellum.evaluations.constants import DEFAULT_MAX_POLLING_DURATION_MS, DEFAULT_POLLING_INTERVAL_MS
from vellum.evaluations.exceptions import TestSuiteRunResultsException
from vellum.evaluations.utils.env import get_api_key
from vellum.evaluations.utils.paginator import PaginatedResults, get_all_results
from vellum.types import (
    ExternalTestCaseExecutionRequest,
    NamedTestCaseVariableValueRequest,
    TestCaseVariableValue,
    TestSuiteRunExecution,
    TestSuiteRunExternalExecConfigDataRequest,
    TestSuiteRunExternalExecConfigRequest,
    TestSuiteRunMetricOutput,
    TestSuiteRunState,
)
from vellum.utils.typing import cast_not_optional
from vellum.utils.uuid import is_valid_uuid

logger = logging.getLogger(__name__)


class VellumTestSuiteRunExecution(TestSuiteRunExecution):
    @classmethod
    def from_api(cls, execution: TestSuiteRunExecution) -> VellumTestSuiteRunExecution:
        return cls(
            id=execution.id,
            test_case_id=execution.test_case_id,
            outputs=execution.outputs,
            metric_results=execution.metric_results,
        )

    def get_metric_output(
        self,
        metric_identifier: str | None = None,
        output_identifier: str | None = None,
    ) -> TestSuiteRunMetricOutput:
        """Retrieve a metric's output by specifying the info needed to uniquely identify that metric and output.

        metric_identifier: Anything that uniquely identifies the metric to retrieve (e.g. it's label, name or id)
        output_identifier: Anything that uniquely identifies the output to retrieve (e.g. it's name)
        """

        metric_outputs = self.get_metric_outputs(metric_identifier)

        filtered_metric_outputs = [
            metric_output
            for metric_output in metric_outputs
            if output_identifier is None or metric_output.name == output_identifier
        ]

        if len(filtered_metric_outputs) == 0:
            raise TestSuiteRunResultsException(f"No metric outputs found with identifier: {output_identifier}")

        if len(filtered_metric_outputs) > 1:
            raise TestSuiteRunResultsException(f"Multiple metric outputs found with identifier: {output_identifier}")

        return filtered_metric_outputs[0]

    def get_metric_outputs(
        self,
        metric_identifier: str | None = None,
    ) -> List[TestSuiteRunMetricOutput]:
        """Return a metric's output across all executions by providing the info needed to uniquely identify it.

        metric_identifier: Anything that uniquely identifies the metric to retrieve (e.g. it's label, name or id).
        """

        filtered_metric_results = [
            metric_output
            for metric_output in self.metric_results
            if metric_identifier is None
            or (metric_output.metric_id == metric_identifier)
            or (metric_output.metric_label == metric_identifier)
            or (metric_output.metric_definition and metric_output.metric_definition.id == metric_identifier)
            or (metric_output.metric_definition and metric_output.metric_definition.name == metric_identifier)
            or (metric_output.metric_definition and metric_output.metric_definition.label == metric_identifier)
        ]

        if len(filtered_metric_results) == 0:
            raise TestSuiteRunResultsException(f"No metric results found with identifier: {metric_identifier}")

        if len(filtered_metric_results) > 1:
            raise TestSuiteRunResultsException(f"Multiple metric results found with identifier: {metric_identifier}")

        return filtered_metric_results[0].outputs


class VellumTestSuiteRunResults:
    """A utility class with methods for conveniently operating on a Test Suite Run and its results."""

    def __init__(
        self,
        test_suite_run: TestSuiteRunRead,
        *,
        client: Vellum | None = None,
        polling_interval: int = DEFAULT_POLLING_INTERVAL_MS,
        max_polling_duration: int = DEFAULT_MAX_POLLING_DURATION_MS,
    ) -> None:
        self._test_suite_run = test_suite_run
        self._client = client or Vellum(
            api_key=get_api_key(),
        )
        self._executions: Generator[VellumTestSuiteRunExecution, None, None] | None = None
        self._polling_interval = polling_interval
        self._max_polling_duration = max_polling_duration

    @property
    def state(self) -> TestSuiteRunState:
        return self._test_suite_run.state

    @cached_property
    def all_executions(self) -> list[VellumTestSuiteRunExecution]:
        return list(self._get_test_suite_run_executions())

    def get_metric_outputs(
        self, metric_identifier: str | None = None, output_identifier: str | None = None
    ) -> List[TestSuiteRunMetricOutput]:
        """Retrieve a metric's output across all executions by providing the info needed to uniquely identify it."""

        return [
            execution.get_metric_output(metric_identifier=metric_identifier, output_identifier=output_identifier)
            for execution in self.all_executions
        ]

    def get_count_metric_outputs(
        self,
        metric_identifier: str | None = None,
        output_identifier: str | None = None,
        *,
        predicate: Callable[[TestSuiteRunMetricOutput], bool] | None = None,
    ) -> int:
        """Returns the count of all metric outputs that match the given criteria."""

        metric_outputs = self.get_metric_outputs(
            metric_identifier=metric_identifier, output_identifier=output_identifier
        )

        if predicate is None:
            return len(metric_outputs)

        return len([output for output in metric_outputs if predicate(output)])

    def get_numeric_metric_output_values(
        self,
        metric_identifier: str | None = None,
        output_identifier: str | None = None,
    ) -> List[float | None]:
        """Returns the values of a numeric metric output that match the given criteria."""

        metric_outputs: list[TestSuiteRunMetricNumberOutput] = []

        for output in self.get_metric_outputs(metric_identifier=metric_identifier, output_identifier=output_identifier):
            if output.type != "NUMBER":
                raise TestSuiteRunResultsException(
                    f"Expected a numeric metric output, but got a {output.type} output instead."
                )

            metric_outputs.append(output)

        return [output.value for output in metric_outputs]

    def get_mean_metric_output(
        self, metric_identifier: str | None = None, output_identifier: str | None = None
    ) -> float:
        """Returns the mean of all metric outputs that match the given criteria."""
        output_values = self.get_numeric_metric_output_values(
            metric_identifier=metric_identifier, output_identifier=output_identifier
        )
        return sum(cast(Iterable[float], filter(lambda o: isinstance(o, float), output_values))) / len(output_values)

    def get_min_metric_output(
        self, metric_identifier: str | None = None, output_identifier: str | None = None
    ) -> float:
        """Returns the min value across= all metric outputs that match the given criteria."""
        output_values = self.get_numeric_metric_output_values(
            metric_identifier=metric_identifier, output_identifier=output_identifier
        )
        return min(cast(Iterable[float], filter(lambda o: isinstance(o, float), output_values)))

    def get_max_metric_output(
        self, metric_identifier: str | None = None, output_identifier: str | None = None
    ) -> float:
        """Returns the max value across all metric outputs that match the given criteria."""
        output_values = self.get_numeric_metric_output_values(
            metric_identifier=metric_identifier, output_identifier=output_identifier
        )
        return max(cast(Iterable[float], filter(lambda o: isinstance(o, float), output_values)))

    def wait_until_complete(self) -> None:
        """Wait until the Test Suite Run is no longer in a QUEUED or RUNNING state."""

        start_time = time.time_ns()
        while True:
            logger.debug("Polling for latest test suite run state...")
            self._refresh_test_suite_run()
            if self.state not in {"QUEUED", "RUNNING"}:
                break

            current_time = time.time_ns()
            if ((current_time - start_time) / 1e6) > self._max_polling_duration:
                raise TestSuiteRunResultsException("Test suite run timed out polling for executions")

            time.sleep(self._polling_interval / 1000.0)

        if self.state == "FAILED":
            raise TestSuiteRunResultsException("Test suite run failed")

        if self.state == "CANCELLED":
            raise TestSuiteRunResultsException("Test suite run was cancelled")

    def _refresh_test_suite_run(self):
        test_suite_run = self._client.test_suite_runs.retrieve(self._test_suite_run.id)
        self._test_suite_run = test_suite_run

    def _list_paginated_executions(
        self, offset: int | None, limit: int | None
    ) -> PaginatedResults[TestSuiteRunExecution]:
        response = self._client.test_suite_runs.list_executions(
            self._test_suite_run.id,
            offset=offset,
            limit=limit,
            expand=[
                "results.metric_results.metric_definition",
                "results.metric_results.metric_label",
            ],
        )
        return PaginatedResults(results=response.results, count=response.count)

    def _wrap_api_executions(
        self, executions: Generator[TestSuiteRunExecution, None, None]
    ) -> Generator[VellumTestSuiteRunExecution, None, None]:
        for execution in executions:
            yield VellumTestSuiteRunExecution.from_api(execution)

    def _get_test_suite_run_executions(
        self,
    ) -> Generator[VellumTestSuiteRunExecution, None, None]:
        if self._executions is not None:
            return self._executions

        self.wait_until_complete()

        raw_api_executions = get_all_results(self._list_paginated_executions)
        self._executions = self._wrap_api_executions(raw_api_executions)
        return self._executions


class VellumTestSuite:
    """A utility class that provides methods for running a Vellum Test Suite and interacting with its results."""

    _test_suite_id: str | None
    _test_suite_name: str | None

    def __init__(
        self,
        test_suite_identifier: str | UUID,
        *,
        client: Vellum | None = None,
    ) -> None:
        self.client = client or Vellum(
            api_key=get_api_key(),
        )

        if is_valid_uuid(test_suite_identifier):
            self._test_suite_id = str(test_suite_identifier)
            self._test_suite_name = None
        else:
            self._test_suite_id = None
            self._test_suite_name = str(test_suite_identifier)

    def run_external(
        self,
        executable: Callable[[List[TestCaseVariableValue]], List[NamedTestCaseVariableValueRequest]],
    ) -> VellumTestSuiteRunResults:
        """
        Runs this Vellum Test Suite on any executable function defined external to Vellum.

        Returns a wrapper that polls the generated Test Suite Run until it's done running and returns its results.
        """
        test_cases = self.client.test_suites.list_test_suite_test_cases(
            id=cast_not_optional(self._test_suite_id or self._test_suite_name)
        )
        executions: List[ExternalTestCaseExecutionRequest] = []

        for test_case in test_cases.results:
            outputs = executable(test_case.input_values)

            executions.append(
                ExternalTestCaseExecutionRequest(
                    test_case_id=test_case.id,  # type: ignore[arg-type]
                    outputs=outputs,
                )
            )

        test_suite_run = self.client.test_suite_runs.create(
            test_suite_id=self._test_suite_id or OMIT,
            test_suite_name=self._test_suite_name or OMIT,
            exec_config=TestSuiteRunExternalExecConfigRequest(
                type="EXTERNAL",
                data=TestSuiteRunExternalExecConfigDataRequest(
                    executions=executions,
                ),
            ),
        )
        return VellumTestSuiteRunResults(test_suite_run, client=self.client)
