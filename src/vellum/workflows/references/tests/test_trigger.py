import pytest
from typing import Optional

from vellum.workflows import BaseWorkflow
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.triggers.base import BaseTrigger


class TestTrigger(BaseTrigger):
    """A test trigger with a message attribute."""

    message: str


class OptionalTrigger(BaseTrigger):
    """A test trigger with an optional message attribute."""

    optional_message: Optional[str]


class SearchNode(BaseNode):
    """Node that uses trigger attribute in an expression."""

    query = TestTrigger.message + " additional search terms"

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"Searched for: {self.query}")


class TriggerExpressionWorkflow(BaseWorkflow):
    """Workflow with a node that uses trigger attribute in an expression."""

    graph = TestTrigger >> SearchNode

    class Outputs(BaseWorkflow.Outputs):
        result = SearchNode.Outputs.result


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


def test_workflow_with_trigger_attribute_in_expression():
    """
    Tests that a workflow with a node using trigger attribute in an expression executes successfully.

    This reproduces a production bug where a node like:
        class SearchMarketData(WebSearchNode[State]):
            query = Chat.message + " home trade-in value market data"
    would fail with TypeError when initializing because trigger_attributes was None.
    """
    # GIVEN a workflow with a node that uses trigger attribute in an AddExpression
    workflow = TriggerExpressionWorkflow()

    # AND a trigger instance with the message attribute
    trigger = TestTrigger(message="test query")

    # WHEN we run the workflow with the trigger
    result = workflow.run(trigger=trigger)

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"

    # AND the node should have concatenated the trigger attribute with the suffix
    assert result.outputs.result == "Searched for: test query additional search terms"
