import pytest
from uuid import uuid4

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.runner.runner import WorkflowRunner
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.workflows.base import BaseWorkflow


class FailingResolver(BaseWorkflowResolver):
    """A resolver that always fails to load state."""

    def load_state(self, previous_execution_id=None):
        return None

    def get_latest_execution_events(self):
        return iter([])

    def get_state_snapshot_history(self):
        return iter([])


class ExceptionThrowingResolver(BaseWorkflowResolver):
    """A resolver that throws an exception when trying to load state."""

    def load_state(self, previous_execution_id=None):
        raise Exception("Resolver failed")

    def get_latest_execution_events(self):
        return iter([])

    def get_state_snapshot_history(self):
        return iter([])


class TestNode(BaseNode):
    class Outputs(BaseOutputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="test")


class TestWorkflowWithFailingResolver(BaseWorkflow):
    graph = TestNode
    resolvers = [FailingResolver()]


class TestWorkflowWithExceptionThrowingResolver(BaseWorkflow):
    graph = TestNode
    resolvers = [ExceptionThrowingResolver()]


class TestWorkflowWithMultipleFailingResolvers(BaseWorkflow):
    graph = TestNode
    resolvers = [FailingResolver(), ExceptionThrowingResolver()]


class TestWorkflowWithNoResolvers(BaseWorkflow):
    graph = TestNode
    resolvers = []


def test_workflow_initialization_exception_when_resolver_returns_none():
    """
    Tests that WorkflowInitializationException is raised when resolver returns None.
    """

    workflow = TestWorkflowWithFailingResolver()

    previous_execution_id = str(uuid4())

    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    assert "All resolvers failed to load initial state" in str(exc_info.value)

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS

    assert exc_info.value.definition == TestWorkflowWithFailingResolver


def test_workflow_initialization_exception_when_resolver_throws_exception():
    """
    Tests that WorkflowInitializationException is raised when resolver throws an exception.
    """

    workflow = TestWorkflowWithExceptionThrowingResolver()

    previous_execution_id = str(uuid4())

    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    assert "All resolvers failed to load initial state" in str(exc_info.value)

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS


def test_workflow_initialization_exception_when_multiple_resolvers_fail():
    """
    Tests that WorkflowInitializationException is raised when multiple resolvers all fail.
    """

    workflow = TestWorkflowWithMultipleFailingResolvers()

    previous_execution_id = str(uuid4())

    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    assert "All resolvers failed to load initial state" in str(exc_info.value)

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS


def test_workflow_initialization_exception_when_no_resolvers_and_previous_execution_id():
    """
    Tests that WorkflowInitializationException is raised when no resolvers are configured
    but previous_execution_id is provided.
    """

    workflow = TestWorkflowWithNoResolvers()

    previous_execution_id = str(uuid4())

    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    assert "No resolvers configured to load initial state" in str(exc_info.value)

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS


def test_no_exception_when_no_resolvers_configured():
    """
    Tests that no exception is raised when workflow has no resolvers configured and no previous_execution_id.
    """

    workflow = TestWorkflowWithNoResolvers()

    runner = WorkflowRunner(workflow=workflow)

    assert runner is not None

    assert set(runner._entrypoints) == set(workflow.get_entrypoints())


def test_no_exception_when_no_previous_execution_id():
    """
    Tests that no exception is raised when no previous execution ID is provided.
    """

    workflow = TestWorkflowWithFailingResolver()

    runner = WorkflowRunner(workflow=workflow)

    assert runner is not None

    assert runner._initial_state is not None


def test_workflow_constructor_accepts_execution_id():
    """
    Tests that execution_id can be passed to the workflow constructor.
    """

    execution_id = uuid4()

    workflow = TestWorkflowWithNoResolvers(execution_id=execution_id)

    assert workflow._execution_id == execution_id


def test_workflow_uses_constructor_execution_id_as_span_id():
    """
    Tests that execution_id from constructor sets the span_id in workflow events.
    """

    execution_id = uuid4()
    workflow = TestWorkflowWithNoResolvers(execution_id=execution_id)

    result = workflow.run()

    assert result.span_id == execution_id


def test_workflow_run_previous_execution_id_overrides_constructor_execution_id():
    """
    Tests that previous_execution_id parameter in run() overrides constructor execution_id.
    """

    constructor_execution_id = uuid4()
    workflow = TestWorkflowWithNoResolvers(execution_id=constructor_execution_id)

    run_execution_id = str(uuid4())

    # THEN it should raise an exception because no resolvers are configured
    with pytest.raises(WorkflowInitializationException) as exc_info:
        workflow.run(previous_execution_id=run_execution_id)

    # AND the error message should mention no resolvers configured
    assert "No resolvers configured to load initial state" in str(exc_info.value)


class TestSlackTrigger(IntegrationTrigger):
    """Test Slack trigger for deserialize_trigger tests."""

    message: str
    channel: str

    class Config(IntegrationTrigger.Config):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_test"


class WorkflowWithInputsInputs(BaseInputs):
    user_query: str
    count: int = 0


class WorkflowWithInputs(BaseWorkflow[WorkflowWithInputsInputs, BaseState]):
    """Test workflow with custom inputs."""

    graph = TestNode


class WorkflowWithSlackTrigger(BaseWorkflow):
    """Test workflow with Slack trigger."""

    graph = TestSlackTrigger >> TestNode


class WorkflowWithMultipleTriggers(BaseWorkflow):
    """Test workflow with multiple triggers."""

    graph = {
        ManualTrigger >> TestNode,
        TestSlackTrigger >> TestNode,
    }


def test_deserialize_trigger__returns_inputs_when_trigger_id_is_none():
    """
    Tests that deserialize_trigger returns workflow Inputs instance when trigger_id is None.
    """

    result = WorkflowWithInputs.deserialize_trigger(trigger_id=None, inputs={"user_query": "test query", "count": 5})

    assert isinstance(result, WorkflowWithInputsInputs)

    assert result.user_query == "test query"
    assert result.count == 5


def test_deserialize_trigger__returns_inputs_with_defaults_when_trigger_id_is_none():
    """
    Tests that deserialize_trigger returns workflow Inputs with default values when trigger_id is None.
    """

    result = WorkflowWithInputs.deserialize_trigger(trigger_id=None, inputs={"user_query": "test query"})

    assert isinstance(result, WorkflowWithInputsInputs)

    assert result.user_query == "test query"
    assert result.count == 0


def test_deserialize_trigger__returns_trigger_instance_when_trigger_id_matches():
    """
    Tests that deserialize_trigger returns trigger instance when trigger_id matches a workflow trigger.
    """

    trigger_id = TestSlackTrigger.__id__

    result = WorkflowWithSlackTrigger.deserialize_trigger(
        trigger_id=trigger_id, inputs={"message": "Hello", "channel": "#general"}
    )

    assert isinstance(result, TestSlackTrigger)

    assert result.message == "Hello"
    assert result.channel == "#general"


def test_deserialize_trigger__returns_trigger_instance_from_multi_trigger_workflow():
    """
    Tests that deserialize_trigger returns correct trigger instance from workflow with multiple triggers.
    """

    trigger_id = TestSlackTrigger.__id__

    result = WorkflowWithMultipleTriggers.deserialize_trigger(
        trigger_id=trigger_id, inputs={"message": "Multi-trigger test", "channel": "#test"}
    )

    assert isinstance(result, TestSlackTrigger)

    assert result.message == "Multi-trigger test"
    assert result.channel == "#test"


def test_deserialize_trigger__raises_error_when_trigger_id_not_found():
    """
    Tests that deserialize_trigger raises WorkflowInitializationException when trigger_id doesn't match.
    """

    non_existent_trigger_id = uuid4()

    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowWithSlackTrigger.deserialize_trigger(trigger_id=non_existent_trigger_id, inputs={"message": "test"})

    assert "No trigger class found" in str(exc_info.value)
    assert str(non_existent_trigger_id) in str(exc_info.value)
