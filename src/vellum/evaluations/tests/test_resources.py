import datetime as dt
from unittest.mock import MagicMock

from vellum.client.types.test_suite_run_execution_metric_result import TestSuiteRunExecutionMetricResult
from vellum.client.types.test_suite_run_metric_number_output import TestSuiteRunMetricNumberOutput
from vellum.client.types.test_suite_run_read import TestSuiteRunRead
from vellum.client.types.test_suite_run_test_suite import TestSuiteRunTestSuite
from vellum.evaluations.resources import VellumTestSuiteRunExecution, VellumTestSuiteRunResults


class TestVellumTestSuiteRunResults:
    """Tests for VellumTestSuiteRunResults."""

    def _build_results(self, values):
        executions = [
            VellumTestSuiteRunExecution(
                id=f"execution-{index}",
                test_case_id=f"test-case-{index}",
                outputs=[],
                metric_results=[
                    TestSuiteRunExecutionMetricResult(
                        metric_id="metric-id",
                        outputs=[TestSuiteRunMetricNumberOutput(name="score", type="NUMBER", value=value)],
                    )
                ],
            )
            for index, value in enumerate(values)
        ]

        results = VellumTestSuiteRunResults(
            test_suite_run=TestSuiteRunRead(
                id="test-suite-run-id",
                created=dt.datetime(2024, 1, 1),
                test_suite=TestSuiteRunTestSuite(id="test-suite-id", history_item_id="history-item-id", label="Suite"),
                state="COMPLETE",
            ),
            client=MagicMock(),
        )
        results.__dict__["all_executions"] = executions
        return results

    def test_get_mean_metric_output__ignores_unpopulated_values(self):
        """Executions that produced no score must not be counted in the denominator of the mean."""

        results = self._build_results([1.0, None, 1.0, None])

        assert results.get_mean_metric_output() == 1.0
