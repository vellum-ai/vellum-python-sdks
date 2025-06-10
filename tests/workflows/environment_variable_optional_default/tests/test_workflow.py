from tests.workflows.environment_variable_optional_default.workflow import OptionalDefaultEnvironmentVariableWorkflow


def test_run_workflow__optional_default_empty_string(monkeypatch):
    monkeypatch.delenv("MISSING_ENV_VAR", raising=False)

    workflow = OptionalDefaultEnvironmentVariableWorkflow()

    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    assert terminal_event.outputs == {}


def test_run_workflow__optional_default_with_env_var(monkeypatch):
    monkeypatch.setenv("MISSING_ENV_VAR", "test_value")

    workflow = OptionalDefaultEnvironmentVariableWorkflow()

    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    assert terminal_event.outputs == {"final_value": "test_value"}
