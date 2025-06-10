from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext


def test_environment_variable_reference_with_context():
    context = WorkflowContext(environment_variables={"TEST_VAR": "test_value"})

    state = BaseState()
    state.context = context

    env_ref = EnvironmentVariableReference(name="TEST_VAR")

    assert env_ref.resolve(state) == "test_value"


def test_environment_variable_reference_fallback_to_os_environ():
    import os

    os.environ["FALLBACK_VAR"] = "fallback_value"

    context = WorkflowContext(environment_variables={})
    state = BaseState()
    state.context = context

    env_ref = EnvironmentVariableReference(name="FALLBACK_VAR")

    assert env_ref.resolve(state) == "fallback_value"

    del os.environ["FALLBACK_VAR"]


def test_environment_variable_reference_with_default():
    context = WorkflowContext(environment_variables={})
    state = BaseState()
    state.context = context

    env_ref = EnvironmentVariableReference(name="NONEXISTENT_VAR", default="default_value")

    assert env_ref.resolve(state) == "default_value"


def test_environment_variable_reference_context_overrides_os_environ():
    import os

    os.environ["OVERRIDE_VAR"] = "os_value"

    context = WorkflowContext(environment_variables={"OVERRIDE_VAR": "context_value"})
    state = BaseState()
    state.context = context

    env_ref = EnvironmentVariableReference(name="OVERRIDE_VAR")

    assert env_ref.resolve(state) == "context_value"

    del os.environ["OVERRIDE_VAR"]
