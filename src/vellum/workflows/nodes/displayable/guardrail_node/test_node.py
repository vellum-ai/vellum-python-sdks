import pytest

from vellum import TestSuiteRunMetricNumberOutput
from vellum.client.types.metric_definition_execution import MetricDefinitionExecution
from vellum.client.types.test_suite_run_metric_string_output import TestSuiteRunMetricStringOutput
from vellum.workflows.nodes.displayable.guardrail_node.node import GuardrailNode


@pytest.mark.parametrize("log_value", [None, ""], ids=["None", "Empty"])
def test_run_guardrail_node__empty_log(vellum_client, log_value):
    """Confirm that we can successfully invoke a Guardrail Node"""

    # GIVEN a Guardrail Node
    class MyGuard(GuardrailNode):
        metric_definition = "example_metric_definition"
        metric_inputs = {}

    # AND we know that the guardrail node will return a blank log
    mock_metric_execution = MetricDefinitionExecution(
        outputs=[
            TestSuiteRunMetricNumberOutput(
                name="score",
                value=0.6,
            ),
            TestSuiteRunMetricStringOutput(
                name="log",
                value=log_value,
            ),
        ],
    )
    vellum_client.metric_definitions.execute_metric_definition.return_value = mock_metric_execution

    # WHEN we run the Guardrail Node
    outputs = MyGuard().run()

    # THEN the workflow should have completed successfully
    assert outputs.score == 0.6
    assert outputs.log == ""
