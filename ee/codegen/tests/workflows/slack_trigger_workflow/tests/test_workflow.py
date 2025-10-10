"""Tests for SlackTrigger workflow."""

from ..workflow import SlackTriggerWorkflow


def test_slack_trigger_workflow__basic_execution():
    """Test that SlackTrigger workflow can be instantiated."""
    # GIVEN a workflow with SlackTrigger
    # WHEN we instantiate it
    workflow = SlackTriggerWorkflow()

    # THEN it should instantiate successfully without errors
    assert workflow is not None
    assert hasattr(workflow, "run")


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


def test_slack_trigger_workflow__trigger_attribute_reference():
    """Test that nodes can reference trigger attributes."""
    from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

    # GIVEN the SlackTrigger workflow
    # WHEN we serialize it
    result = get_workflow_display(workflow_class=SlackTriggerWorkflow).serialize()

    # THEN it should have nodes
    assert "workflow_raw_data" in result
    workflow_data = result["workflow_raw_data"]
    assert isinstance(workflow_data, dict)
    assert "nodes" in workflow_data
    nodes = workflow_data["nodes"]
    assert isinstance(nodes, list)

    # Find the ProcessMessageNode
    process_node = None
    for node in nodes:
        assert isinstance(node, dict)
        # For GENERIC type nodes, the label is at the top level
        if node.get("label") == "Process Message Node":
            process_node = node
            break

    assert process_node is not None, "ProcessMessageNode should exist in serialized workflow"

    # Check that ProcessMessageNode has outputs that reference trigger attribute
    assert "outputs" in process_node
    outputs = process_node["outputs"]
    assert isinstance(outputs, list)

    # Find the processed_message output
    processed_message_output = None
    for output in outputs:
        assert isinstance(output, dict)
        if output.get("name") == "processed_message":
            processed_message_output = output
            break

    assert processed_message_output is not None, "processed_message output should exist"

    # Verify the output references a trigger attribute
    assert "value" in processed_message_output
    value = processed_message_output["value"]
    assert isinstance(value, dict)
    assert value.get("type") == "TRIGGER_ATTRIBUTE"
    assert "triggerId" in value
    assert "attributeId" in value
