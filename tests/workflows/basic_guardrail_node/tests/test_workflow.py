from vellum import StringInput, TestSuiteRunMetricNumberOutput
from vellum.client.types.metric_definition_execution import MetricDefinitionExecution
from vellum.workflows.constants import LATEST_RELEASE_TAG

from tests.workflows.basic_guardrail_node.workflow import BasicGuardrailNodeWorkflow, Inputs


def test_run_workflow__happy_path(vellum_client):
    """Confirm that we can successfully invoke a Workflow with a single Guardrail Node"""

    # GIVEN a workflow that's set up to hit a Guardrail Node
    workflow = BasicGuardrailNodeWorkflow()

    # AND we know what the Guardrail Node will respond with
    mock_metric_execution = MetricDefinitionExecution(
        outputs=[
            TestSuiteRunMetricNumberOutput(
                name="score",
                value=0.6,
            )
        ],
    )
    vellum_client.metric_definitions.execute_metric_definition.return_value = mock_metric_execution

    # WHEN we run the workflow
    terminal_event = workflow.run(
        inputs=Inputs(
            actual="Value from API",
            expected="Value I wanted from API",
        )
    )

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs == {"score": 0.6}

    # AND we should have invoked the Workflow Deployment with the expected inputs
    vellum_client.metric_definitions.execute_metric_definition.assert_called_once_with(
        "example_metric_definition",
        inputs=[
            StringInput(name="expected", value="Value I wanted from API"),
            StringInput(name="actual", value="Value from API"),
        ],
        release_tag=LATEST_RELEASE_TAG,
        request_options=None,
    )
