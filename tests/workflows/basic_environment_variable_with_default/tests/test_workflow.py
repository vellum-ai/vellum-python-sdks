import os

from tests.workflows.basic_environment_variable_with_default.workflow import BasicEnvironmentVariableWorkflow


def test_environment_variable_workflow_defaults():
    # Ensure no relevant environment variables are set
    os.environ.pop("API_URL", None)

    # GIVEN a workflow that references unset environment variables
    workflow = BasicEnvironmentVariableWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN it should use the default values
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    assert terminal_event.outputs == {"final_value": "https://default.api.vellum.ai"}
