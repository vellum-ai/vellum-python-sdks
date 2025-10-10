"""Tests for SlackTrigger workflow."""

from ..workflow import SlackTriggerWorkflow


def test_slack_trigger_workflow__basic_execution():
    """Test that SlackTrigger workflow can be instantiated and executed."""
    # GIVEN a workflow with SlackTrigger
    workflow = SlackTriggerWorkflow()

    # WHEN we run the workflow
    result = workflow.run()

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"
    assert result.outputs.result == "Processed Slack message"


def test_slack_trigger_workflow__has_trigger():
    """Test that workflow has SlackTrigger in its graph."""
    # GIVEN the SlackTrigger workflow
    # WHEN we check its subgraphs
    subgraphs = SlackTriggerWorkflow.get_subgraphs()

    # THEN it should have trigger edges
    has_trigger = False
    for subgraph in subgraphs:
        if list(subgraph.trigger_edges):
            has_trigger = True
            break

    assert has_trigger, "Workflow should have trigger edges"


def test_slack_trigger_workflow__serialization():
    """Test that workflow with SlackTrigger can be serialized."""
    from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

    # GIVEN the SlackTrigger workflow
    # WHEN we serialize it
    result = get_workflow_display(workflow_class=SlackTriggerWorkflow).serialize()

    # THEN it should have triggers
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1

    # AND the trigger should be SLACK_MESSAGE type
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    assert trigger["type"] == "SLACK_MESSAGE"

    # AND the trigger should have attributes
    assert "attributes" in trigger
    attributes = trigger["attributes"]
    assert isinstance(attributes, list)
    assert len(attributes) == 6  # All SlackTrigger attribute fields
