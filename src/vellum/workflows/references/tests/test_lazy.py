import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.lazy import LazyReference


class ResponseNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        response: str = "Hello from node!"


class TestWorkflowWithOutput(BaseWorkflow):
    graph = ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        final_response = ResponseNode.Outputs.response


class TestWorkflowWithLiteralOutput(BaseWorkflow):
    graph = ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        literal_value = "Hello literal!"


@pytest.fixture
def mock_inspect_getsource(mocker):
    return mocker.patch("inspect.getsource")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("vellum.workflows.references.lazy.logger")


def test_lazy_reference__inspect_getsource_fails(mock_inspect_getsource, mock_logger):
    # GIVEN getsource fails to resolve the lambda's source code
    mock_inspect_getsource.side_effect = Exception("test")

    # WHEN a node with a lazy reference is defined
    class MyNode(BaseNode):
        lazy_reference = LazyReference(lambda: MyNode.Outputs.foo)

    # THEN the name is the lambda function's name
    assert MyNode.lazy_reference.instance
    assert MyNode.lazy_reference.instance.name == "<lambda>"

    # AND sentry is notified
    assert mock_logger.exception.call_count == 1


def test_lazy_reference__string_resolves_workflow_output():
    """Tests that string-based LazyReference can resolve workflow output references."""

    # GIVEN a workflow with an output that references a node output (defined at module level)
    # WHEN we run the workflow
    terminal_event = TestWorkflowWithOutput().run()

    # THEN the workflow completes successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.final_state is not None

    # AND we can resolve a string-based LazyReference to the workflow output
    lazy_ref = LazyReference[str]("TestWorkflowWithOutput.Outputs.final_response")
    resolved_value = lazy_ref.resolve(terminal_event.final_state)

    # THEN the resolved value matches the node output
    assert resolved_value == "Hello from node!"


def test_lazy_reference__string_resolves_literal_workflow_output():
    """Tests that string-based LazyReference can resolve literal workflow output values."""

    # GIVEN a workflow with a literal output value (defined at module level)
    # WHEN we run the workflow
    terminal_event = TestWorkflowWithLiteralOutput().run()

    # THEN the workflow completes successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.final_state is not None

    # AND we can resolve a string-based LazyReference to the literal workflow output
    lazy_ref = LazyReference[str]("TestWorkflowWithLiteralOutput.Outputs.literal_value")
    resolved_value = lazy_ref.resolve(terminal_event.final_state)

    # THEN the resolved value matches the literal output
    assert resolved_value == "Hello literal!"
