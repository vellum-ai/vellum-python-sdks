import pytest

from vellum import TestSuiteRunMetricNumberOutput
from vellum.client import ApiError
from vellum.client.types.metric_definition_execution import MetricDefinitionExecution
from vellum.client.types.test_suite_run_metric_string_output import TestSuiteRunMetricStringOutput
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
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


def test_run_guardrail_node__normalized_score(vellum_client):
    """Confirm that we can successfully invoke a Guardrail Node"""

    # GIVEN a Guardrail Node
    class MyGuard(GuardrailNode):
        metric_definition = "example_metric_definition"
        metric_inputs = {}

    # AND we know that the guardrail node will return a normalized score
    mock_metric_execution = MetricDefinitionExecution(
        outputs=[
            TestSuiteRunMetricNumberOutput(
                name="score",
                value=0.6,
            ),
            TestSuiteRunMetricNumberOutput(
                name="normalized_score",
                value=1.0,
            ),
        ],
    )
    vellum_client.metric_definitions.execute_metric_definition.return_value = mock_metric_execution

    # WHEN we run the Guardrail Node
    outputs = MyGuard().run()

    # THEN the workflow should have completed successfully
    assert outputs.score == 0.6
    assert outputs.normalized_score == 1.0


def test_run_guardrail_node__normalized_score_null(vellum_client):
    # GIVEN a Guardrail Node
    class MyGuard(GuardrailNode):
        metric_definition = "example_metric_definition"
        metric_inputs = {}

    # AND we know that the guardrail node will return a normalized score that is None
    mock_metric_execution = MetricDefinitionExecution(
        outputs=[
            TestSuiteRunMetricNumberOutput(
                name="score",
                value=0.6,
            ),
            TestSuiteRunMetricNumberOutput(
                name="normalized_score",
                value=None,
            ),
        ],
    )
    vellum_client.metric_definitions.execute_metric_definition.return_value = mock_metric_execution

    # WHEN we run the Guardrail Node
    with pytest.raises(NodeException) as exc_info:
        MyGuard().run()

    # THEN we get an exception
    assert exc_info.value.message == "Metric execution must have one output named 'normalized_score' with type 'float'"
    assert exc_info.value.code == WorkflowErrorCode.INVALID_OUTPUTS


def test_run_guardrail_node__reason(vellum_client):
    # GIVEN a Guardrail Node
    class MyGuard(GuardrailNode):
        metric_definition = "example_metric_definition"
        metric_inputs = {}

    # AND we know that the guardrail node will return a reason
    mock_metric_execution = MetricDefinitionExecution(
        outputs=[
            TestSuiteRunMetricNumberOutput(
                name="score",
                value=0.6,
            ),
            TestSuiteRunMetricStringOutput(
                name="reason",
                value="foo",
            ),
        ],
    )
    vellum_client.metric_definitions.execute_metric_definition.return_value = mock_metric_execution

    # WHEN we run the Guardrail Node
    outputs = MyGuard().run()

    # THEN the workflow should have completed successfully
    assert outputs.score == 0.6
    assert outputs.reason == "foo"


def test_run_guardrail_node__api_error(vellum_client):
    # GIVEN a Guardrail Node
    class MyGuard(GuardrailNode):
        metric_definition = "example_metric_definition"
        metric_inputs = {}

    # AND the API client raises an ApiError when called
    api_error = ApiError(status_code=503)
    vellum_client.metric_definitions.execute_metric_definition.side_effect = api_error

    # WHEN we run the Guardrail Node
    with pytest.raises(NodeException) as exc_info:
        MyGuard().run()

    # THEN we get a NodeException with the appropriate error code
    assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION
    assert "Failed to execute metric definition" in exc_info.value.message

    # Verify the mock was called with the expected arguments
    vellum_client.metric_definitions.execute_metric_definition.assert_called_once_with(
        "example_metric_definition", inputs=[], release_tag="LATEST", request_options=None
    )
