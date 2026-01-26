import pytest
from typing import Optional

from vellum.workflows import BaseWorkflow
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class TestTrigger(BaseTrigger):
    """A test trigger with a message attribute."""

    message: str


class OptionalTrigger(BaseTrigger):
    """A test trigger with an optional message attribute."""

    optional_message: Optional[str]


class ChatTrigger(ChatMessageTrigger):
    """A chat trigger for testing trigger attribute expressions with string message."""

    message: str  # type: ignore[assignment]


class ChatSearchNode(BaseNode):
    """Node that uses chat trigger message attribute in an expression."""

    query = ChatTrigger.message + " home trade-in value market data"

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"Searched for: {self.query}")


class ChatInputs(BaseInputs):
    """Inputs for the chat workflow."""

    message: str


class ChatTriggerExpressionWorkflow(BaseWorkflow[ChatInputs, BaseState]):
    """Workflow with a node that uses chat trigger attribute in an expression."""

    graph = ChatTrigger >> ChatSearchNode

    class Outputs(BaseWorkflow.Outputs):
        result = ChatSearchNode.Outputs.result


def test_trigger_attribute_reference__resolve_with_none_trigger_attributes():
    """
    Tests that TriggerAttributeReference.resolve handles None trigger_attributes gracefully.

    This reproduces a production bug where trigger_attributes being None caused:
    TypeError: argument of type 'NoneType' is not iterable
    """
    # GIVEN a trigger attribute reference
    reference = TestTrigger.message
    assert isinstance(reference, TriggerAttributeReference)

    # AND a state where trigger_attributes is None (the default)
    state = BaseState(meta=StateMeta())
    assert state.meta.trigger_attributes is None

    # WHEN we try to resolve the reference
    # THEN it should raise NodeException (not TypeError)
    with pytest.raises(NodeException) as exc_info:
        reference.resolve(state)

    # AND the error message should be helpful
    assert "Missing trigger attribute" in str(exc_info.value)
    assert "message" in str(exc_info.value)


def test_trigger_attribute_reference__resolve_with_none_trigger_attributes_optional():
    """
    Tests that optional TriggerAttributeReference resolves to None when trigger_attributes is None.
    """
    # GIVEN a trigger attribute reference for the optional attribute
    reference = OptionalTrigger.optional_message
    assert isinstance(reference, TriggerAttributeReference)

    # AND a state where trigger_attributes is None (the default)
    state = BaseState(meta=StateMeta())
    assert state.meta.trigger_attributes is None

    # WHEN we resolve the reference
    result = reference.resolve(state)

    # THEN it should return None (not raise an error)
    assert result is None


def test_workflow_with_chat_trigger_attribute_in_expression():
    """
    Tests that a workflow with a node using ChatMessageTrigger attribute in an expression
    gives a proper error message instead of TypeError when trigger_attributes is None.

    This reproduces a production bug where a node like:
        class SearchMarketData(WebSearchNode[State]):
            query = Chat.message + " home trade-in value market data"
    would fail with TypeError when initializing because trigger_attributes was None
    when the workflow was run with inputs= instead of trigger=.

    After the fix, we get a proper error message instead of TypeError.
    """
    # GIVEN a workflow with a node that uses chat trigger attribute in an AddExpression
    workflow = ChatTriggerExpressionWorkflow()

    # WHEN we run the workflow with inputs (which previously caused TypeError)
    result = workflow.run(inputs=ChatInputs(message="test query"))

    # THEN the workflow should be rejected with a proper error message (not TypeError)
    assert result.name == "workflow.execution.rejected"

    # AND the error message should be helpful (not "argument of type 'NoneType' is not iterable")
    assert "Missing trigger attribute" in result.error.message
    assert "message" in result.error.message
    assert "ChatTrigger" in result.error.message
