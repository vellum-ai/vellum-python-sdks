import pytest
import sys
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


def test_workflow_falls_back_to_default_state_when_resolver_returns_none():
    """
    Tests that workflow falls back to default state when resolver returns None.
    """

    workflow = TestWorkflowWithFailingResolver()

    previous_execution_id = str(uuid4())

    # WHEN we create a runner with a previous_execution_id but resolver returns None
    runner = WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    # THEN the runner should be created successfully with default state
    assert runner is not None
    assert runner._initial_state is not None


def test_workflow_falls_back_to_default_state_when_resolver_throws_exception():
    """
    Tests that workflow falls back to default state when resolver throws an exception.
    """

    workflow = TestWorkflowWithExceptionThrowingResolver()

    previous_execution_id = str(uuid4())

    # WHEN we create a runner with a previous_execution_id but resolver throws exception
    runner = WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    # THEN the runner should be created successfully with default state
    assert runner is not None
    assert runner._initial_state is not None


def test_workflow_falls_back_to_default_state_when_multiple_resolvers_fail():
    """
    Tests that workflow falls back to default state when multiple resolvers all fail.
    """

    workflow = TestWorkflowWithMultipleFailingResolvers()

    previous_execution_id = str(uuid4())

    # WHEN we create a runner with a previous_execution_id but all resolvers fail
    runner = WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    # THEN the runner should be created successfully with default state
    assert runner is not None
    assert runner._initial_state is not None


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


def test_workflow_uses_constructor_execution_id_as_span_id():
    """
    Tests that execution_id parameter in run() sets the span_id in workflow events.
    """

    workflow = TestWorkflowWithNoResolvers()

    # AND an execution_id
    execution_id = uuid4()

    # WHEN we run the workflow with execution_id
    result = workflow.run(execution_id=execution_id)

    # THEN the result span_id should match the execution_id
    assert result.span_id == execution_id


def test_workflow_run_previous_execution_id_overrides_constructor_execution_id():
    """
    Tests that previous_execution_id parameter triggers resume behavior.
    """

    workflow = TestWorkflowWithNoResolvers()

    # AND a previous_execution_id
    run_execution_id = str(uuid4())

    # WHEN we run the workflow with previous_execution_id
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


class FailingConstructorTrigger(IntegrationTrigger):
    """Test trigger that fails during construction when required_field is missing."""

    required_field: str

    class Config(IntegrationTrigger.Config):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "TEST"
        slug = "failing_constructor"

    def __init__(self, **kwargs):
        if "required_field" not in kwargs:
            raise ValueError("required_field is required")
        super().__init__(**kwargs)


class WorkflowWithInputsInputs(BaseInputs):
    user_query: str
    count: int = 0


class WorkflowWithInputs(BaseWorkflow[WorkflowWithInputsInputs, BaseState]):
    """Test workflow with custom inputs."""

    graph = TestNode


class WorkflowWithSlackTrigger(BaseWorkflow):
    """Test workflow with Slack trigger."""

    graph = TestSlackTrigger >> TestNode


class WorkflowWithFailingConstructorTrigger(BaseWorkflow):
    """Test workflow with a trigger that fails during construction."""

    graph = FailingConstructorTrigger >> TestNode


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


def test_deserialize_trigger__raises_workflow_initialization_exception_when_trigger_constructor_fails():
    """
    Tests that deserialize_trigger raises WorkflowInitializationException when trigger constructor fails.
    """

    # GIVEN a workflow with a trigger that validates required fields in its constructor
    trigger_id = FailingConstructorTrigger.__id__

    # AND inputs that are missing the required field
    invalid_inputs = {"some_other_field": "value"}

    # WHEN we call deserialize_trigger with invalid inputs
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowWithFailingConstructorTrigger.deserialize_trigger(trigger_id=trigger_id, inputs=invalid_inputs)

    # AND the error message should mention the trigger class name
    assert "Failed to instantiate trigger" in str(exc_info.value)
    assert "FailingConstructorTrigger" in str(exc_info.value)


def test_deserialize_trigger__returns_trigger_instance_when_trigger_name_matches():
    """
    Tests that deserialize_trigger returns trigger instance when trigger_name (non-UUID string) matches.
    """

    # GIVEN a workflow with a Slack trigger that has slug "slack_test"
    # AND the trigger name from __trigger_name__
    trigger_name = TestSlackTrigger.__trigger_name__

    # WHEN we call deserialize_trigger with the trigger name
    result = WorkflowWithSlackTrigger.deserialize_trigger(
        trigger_id=trigger_name, inputs={"message": "Hello by name", "channel": "#general"}
    )

    # THEN it should return the correct trigger instance
    assert isinstance(result, TestSlackTrigger)

    # AND the trigger should have the correct attributes
    assert result.message == "Hello by name"
    assert result.channel == "#general"


def test_deserialize_trigger__returns_trigger_instance_when_uuid_string_matches():
    """
    Tests that deserialize_trigger returns trigger instance when trigger_id is a UUID string.
    """

    # GIVEN a workflow with a Slack trigger
    # AND the trigger ID as a string
    trigger_id_str = str(TestSlackTrigger.__id__)

    # WHEN we call deserialize_trigger with the UUID string
    result = WorkflowWithSlackTrigger.deserialize_trigger(
        trigger_id=trigger_id_str, inputs={"message": "Hello by UUID string", "channel": "#test"}
    )

    # THEN it should return the correct trigger instance
    assert isinstance(result, TestSlackTrigger)

    # AND the trigger should have the correct attributes
    assert result.message == "Hello by UUID string"
    assert result.channel == "#test"


def test_deserialize_trigger__returns_manual_trigger_by_name():
    """
    Tests that deserialize_trigger returns ManualTrigger when trigger_name is "manual".
    """

    # GIVEN a workflow with multiple triggers including ManualTrigger
    # WHEN we call deserialize_trigger with the name "manual"
    result = WorkflowWithMultipleTriggers.deserialize_trigger(trigger_id="manual", inputs={})

    # THEN it should return a ManualTrigger instance
    assert isinstance(result, ManualTrigger)


def test_deserialize_trigger__raises_error_when_trigger_name_not_found():
    """
    Tests that deserialize_trigger raises WorkflowInitializationException when trigger_name doesn't match.
    """

    # GIVEN a workflow with a Slack trigger
    # AND a non-existent trigger name
    non_existent_name = "non_existent_trigger"

    # WHEN we call deserialize_trigger with the non-existent name
    # THEN it should raise WorkflowInitializationException
    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowWithSlackTrigger.deserialize_trigger(trigger_id=non_existent_name, inputs={"message": "test"})

    # AND the error message should mention the trigger name
    assert "No trigger class found with name" in str(exc_info.value)
    assert non_existent_name in str(exc_info.value)

    # AND the error message should list available trigger names
    assert "Available trigger names" in str(exc_info.value)


@pytest.fixture
def virtual_file_loader():
    """Fixture to manage VirtualFileFinder registration and cleanup."""
    try:
        from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder
    except ImportError:
        pytest.skip("vellum_ee not installed")

    finders = []

    def _register(files, namespace, source_module=None):
        finder = VirtualFileFinder(files, namespace, source_module=source_module)
        sys.meta_path.append(finder)
        finders.append(finder)
        return finder

    yield _register

    for finder in reversed(finders):
        if finder in sys.meta_path:
            sys.meta_path.remove(finder)


def test_resolve_node_ref__suffix_matching_with_namespace_prefix(virtual_file_loader):
    """
    Tests that resolve_node_ref correctly resolves node references when the node's
    __module__ has a UUID namespace prefix (as happens with dynamically loaded workflows).

    This tests the fallback path in resolve_node_ref that matches nodes by their
    module path suffix when direct import fails.
    """
    # GIVEN a workflow with nodes in a subpackage
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.my_node import MyNode

class Workflow(BaseWorkflow):
    graph = MyNode
""",
        "nodes/__init__.py": "from .my_node import MyNode",
        "nodes/my_node.py": """\
from vellum.workflows.nodes import BaseNode

class MyNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        greeting: str

    def run(self) -> Outputs:
        return self.Outputs(greeting="Hello, World!")
""",
    }

    # AND the workflow is loaded with a UUID namespace (simulating dynamic loading)
    namespace = str(uuid4())
    virtual_file_loader(files, namespace)

    # WHEN we load the workflow
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow()

    # Verify the node's __module__ has the namespace prefix
    MyNode = workflow.graph
    assert MyNode.__module__.startswith(namespace)
    assert MyNode.__module__ == f"{namespace}.nodes.my_node"

    # AND we call run_node with the module path string (without namespace prefix)
    # This is how the API passes node references: "nodes.my_node.MyNode"
    # The direct import will fail because "nodes.my_node" doesn't exist at the top level,
    # so resolve_node_ref falls back to suffix matching
    events = list(workflow.run_node("nodes.my_node.MyNode"))

    # THEN the node should execute successfully
    assert len(events) >= 2  # At least initiated and fulfilled events

    # AND the last event should be a fulfilled event with the correct output
    fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    assert len(fulfilled_events) == 1

    outputs = fulfilled_events[0].outputs
    assert outputs.greeting == "Hello, World!"
