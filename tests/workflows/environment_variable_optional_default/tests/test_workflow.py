import os

from tests.workflows.environment_variable_optional_default.workflow import OptionalDefaultEnvironmentVariableWorkflow


def test_run_workflow__optional_default_empty_string():
    os.environ.pop("MISSING_ENV_VAR", None)

    workflow = OptionalDefaultEnvironmentVariableWorkflow()

    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    assert terminal_event.outputs == {"final_value": ""}


def test_run_workflow__optional_default_with_env_var():
    os.environ["MISSING_ENV_VAR"] = "test_value"

    try:
        workflow = OptionalDefaultEnvironmentVariableWorkflow()

        terminal_event = workflow.run()

        assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

        assert terminal_event.outputs == {"final_value": "test_value"}
    finally:
        os.environ.pop("MISSING_ENV_VAR", None)
