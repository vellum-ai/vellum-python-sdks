import os

from tests.workflows.basic_environment_variable.workflow import BasicEnvironmentVariableWorkflow


def test_run_workflow__happy_path():
    # GIVEN an environment variable named `API_URL` is set
    os.environ["API_URL"] = "https://api.vellum.ai"

    # AND a workflow that references the environment variable
    workflow = BasicEnvironmentVariableWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the environment variable
    assert terminal_event.outputs == {"final_value": "https://api.vellum.ai"}


def test_run_workflow__missing_environment_variable():
    # Ensure no relevant environment variables are set
    os.environ.pop("API_URL", None)

    # GIVEN a workflow that references an environment variable that is not set
    workflow = BasicEnvironmentVariableWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should fail
    assert terminal_event.name == "workflow.execution.rejected", terminal_event
