"""Tests for duplicate trigger name validation during serialization."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum_ee.workflows.display.utils.exceptions import TriggerValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_duplicate_trigger_names__same_slug_produces_error():
    """
    Tests that two integration triggers with the same slug produce a validation error.
    """

    # GIVEN two IntegrationTrigger subclasses with the same slug
    class SlackTrigger1(IntegrationTrigger):
        message: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    class SlackTrigger2(IntegrationTrigger):
        channel: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    # AND nodes for each trigger
    class ProcessNode1(BaseNode):
        pass

    class ProcessNode2(BaseNode):
        pass

    # AND a workflow with both triggers
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            SlackTrigger1 >> ProcessNode1,
            SlackTrigger2 >> ProcessNode2,
        }

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    workflow_display.serialize()

    # THEN the display_context should contain a TriggerValidationError
    errors = list(workflow_display.display_context.errors)
    trigger_errors = [e for e in errors if isinstance(e, TriggerValidationError)]
    assert len(trigger_errors) == 1

    # AND the error should mention duplicate trigger name
    error = trigger_errors[0]
    assert "Duplicate trigger name" in str(error)
    assert "slack_new_message" in str(error)


def test_different_trigger_names__no_error():
    """
    Tests that two integration triggers with different slugs do not produce a validation error.
    """

    # GIVEN two IntegrationTrigger subclasses with different slugs
    class SlackTrigger(IntegrationTrigger):
        message: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    class GmailTrigger(IntegrationTrigger):
        email: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "GMAIL"
            slug = "gmail_new_email"

    # AND nodes for each trigger
    class ProcessSlack(BaseNode):
        pass

    class ProcessGmail(BaseNode):
        pass

    # AND a workflow with both triggers
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            SlackTrigger >> ProcessSlack,
            GmailTrigger >> ProcessGmail,
        }

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    result: dict = workflow_display.serialize()

    # THEN there should be no TriggerValidationError about duplicate names
    errors = list(workflow_display.display_context.errors)
    duplicate_errors = [
        e for e in errors if isinstance(e, TriggerValidationError) and "Duplicate trigger name" in str(e)
    ]
    assert len(duplicate_errors) == 0

    # AND both triggers should be serialized with their respective names
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 2
    trigger_names = {t["name"] for t in triggers}
    assert trigger_names == {"slack_new_message", "gmail_new_email"}


def test_trigger_name_serialization__chat_trigger():
    """
    Tests that ChatMessageTrigger serializes with name 'chat'.
    """
    from vellum.workflows.triggers.chat_message import ChatMessageTrigger

    # GIVEN a ChatMessageTrigger subclass
    class MyChatTrigger(ChatMessageTrigger):
        pass

    # AND a simple node
    class ProcessNode(BaseNode):
        pass

    # AND a workflow with the chat trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyChatTrigger >> ProcessNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    result: dict = workflow_display.serialize()

    # THEN the trigger should have name 'chat'
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
    assert triggers[0]["name"] == "chat"


def test_trigger_name_serialization__scheduled_trigger():
    """
    Tests that ScheduleTrigger serializes with name 'scheduled'.
    """
    from vellum.workflows.triggers.schedule import ScheduleTrigger

    # GIVEN a ScheduleTrigger subclass
    class MyScheduledTrigger(ScheduleTrigger):
        class Config(ScheduleTrigger.Config):
            cron = "0 9 * * *"
            timezone = "UTC"

    # AND a simple node
    class ProcessNode(BaseNode):
        pass

    # AND a workflow with the scheduled trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyScheduledTrigger >> ProcessNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    result: dict = workflow_display.serialize()

    # THEN the trigger should have name 'scheduled'
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
    assert triggers[0]["name"] == "scheduled"


def test_trigger_name_serialization__integration_trigger():
    """
    Tests that IntegrationTrigger serializes with name equal to its slug.
    """

    # GIVEN an IntegrationTrigger subclass with a specific slug
    class MySlackTrigger(IntegrationTrigger):
        message: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    # AND a simple node
    class ProcessNode(BaseNode):
        pass

    # AND a workflow with the integration trigger
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MySlackTrigger >> ProcessNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    result: dict = workflow_display.serialize()

    # THEN the trigger should have name equal to the slug
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
    assert triggers[0]["name"] == "slack_new_message"
