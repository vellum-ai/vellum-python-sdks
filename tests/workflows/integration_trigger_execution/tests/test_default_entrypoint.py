"""Tests for default entrypoint behavior when no trigger is provided."""

from tests.workflows.integration_trigger_execution.nodes.slack_message_trigger import SlackMessageTrigger
from tests.workflows.integration_trigger_execution.workflows.multi_trigger_workflow import MultiTriggerWorkflow
from tests.workflows.integration_trigger_execution.workflows.routing_only_workflow import RoutingOnlyWorkflow
from tests.workflows.integration_trigger_execution.workflows.simple_workflow import SimpleSlackWorkflow


def test_single_trigger_no_inputs_defaults_to_entrypoint():
    """
    Tests that workflow with single IntegrationTrigger and no inputs defaults to entrypoint.
    """

    workflow = RoutingOnlyWorkflow()

    # WHEN we run the workflow without trigger and without inputs
    result = workflow.run()

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"

    assert result.outputs.result == "Workflow executed successfully"


def test_single_trigger_with_attribute_references_still_fails():
    """
    Tests that workflow referencing trigger attributes still fails without trigger data.
    """

    # GIVEN a workflow with SlackMessageTrigger that references trigger attributes
    workflow = SimpleSlackWorkflow()

    # WHEN we run the workflow without trigger and without inputs
    result = workflow.run()

    assert result.name == "workflow.execution.rejected"

    assert "Missing trigger attribute" in result.body.error.message


def test_multiple_triggers_no_inputs_uses_manual_path():
    """
    Tests that workflow with multiple triggers and no inputs uses ManualTrigger path.
    """

    # GIVEN a workflow with both ManualTrigger and IntegrationTrigger
    workflow = MultiTriggerWorkflow()

    # WHEN we run the workflow without trigger and without inputs
    result = workflow.run()

    # THEN it should execute successfully via ManualTrigger path (existing behavior)
    assert result.name == "workflow.execution.fulfilled"

    assert result.outputs.manual_result == "Manual execution"


def test_explicit_trigger_param_works_unchanged():
    """
    Tests that providing explicit trigger parameter still works as before.
    """

    workflow = SimpleSlackWorkflow()

    # AND a valid Slack trigger instance
    trigger = SlackMessageTrigger(
        message="Explicit trigger test",
        channel="C123456",
        user="U789012",
    )

    # WHEN we run the workflow with the trigger
    result = workflow.run(trigger=trigger)

    # THEN it should execute successfully
    assert result.name == "workflow.execution.fulfilled"

    # AND the node should have access to trigger outputs
    assert result.outputs.result == "Received 'Explicit trigger test' from channel C123456"


def test_single_trigger_no_inputs_stream_works():
    """
    Tests that workflow.stream() with single IntegrationTrigger and no inputs works.
    """

    workflow = RoutingOnlyWorkflow()

    events = list(workflow.stream())

    # THEN we should get workflow events
    assert len(events) > 0

    # AND the final event should be fulfilled
    last_event = events[-1]
    assert last_event.name == "workflow.execution.fulfilled"

    assert last_event.outputs.result == "Workflow executed successfully"
