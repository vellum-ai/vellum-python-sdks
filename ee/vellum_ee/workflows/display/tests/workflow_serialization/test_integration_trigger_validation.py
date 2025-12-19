"""Tests for IntegrationTrigger attribute type validation during serialization."""

import pytest
from unittest.mock import patch

from vellum.client.types.composio_tool_definition import ComposioToolDefinition
from vellum.client.types.integration import Integration
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum_ee.workflows.display.utils.exceptions import TriggerValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class LinearIssueTrigger(IntegrationTrigger):
    """Custom Linear issue trigger for testing."""

    action: str
    data: dict
    type: str
    url: str

    class Config:
        provider = "COMPOSIO"
        integration_name = "LINEAR"
        slug = "LINEAR_ISSUE_CREATED_TRIGGER"
        setup_attributes = {"team_id": "test-team-id"}


class ProcessNode(BaseNode):
    """Node that processes the trigger."""

    class Outputs(BaseNode.Outputs):
        result = LinearIssueTrigger.action

    def run(self) -> Outputs:
        return self.Outputs()


class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    graph = LinearIssueTrigger >> ProcessNode


def _create_mock_tool_definition(output_parameters: dict) -> ComposioToolDefinition:
    """Helper to create a mock tool definition."""
    return ComposioToolDefinition(
        provider="COMPOSIO",
        integration=Integration(id="test-id", provider="COMPOSIO", name="LINEAR"),
        name="LINEAR_ISSUE_CREATED_TRIGGER",
        label="Issue Created Trigger",
        description="Triggered when a new issue is created.",
        input_parameters={},
        output_parameters=output_parameters,
    )


def test_integration_trigger_validation__matching_types():
    """
    Tests that serialization succeeds when trigger attribute types match the API definition.
    """
    # GIVEN a tool definition from the API with matching types
    mock_tool_def = _create_mock_tool_definition(
        {
            "action": {"type": "string"},
            "data": {"type": "json"},
            "type": {"type": "string"},
            "url": {"type": "string"},
        }
    )

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integration_providers,
        "retrieve_integration_provider_tool_definition",
        return_value=mock_tool_def,
    ):
        # THEN serialization should succeed without raising an error
        result = workflow_display.serialize()

    # AND the trigger should be serialized correctly
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1


def test_integration_trigger_validation__type_mismatch():
    """
    Tests that serialization raises TriggerValidationError when attribute types don't match.
    """
    # GIVEN a tool definition from the API with mismatched types
    # The API says 'action' should be JSON, but our trigger defines it as STRING
    mock_tool_def = _create_mock_tool_definition(
        {
            "action": {"type": "json"},
            "data": {"type": "json"},
            "type": {"type": "string"},
            "url": {"type": "string"},
        }
    )

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integration_providers,
        "retrieve_integration_provider_tool_definition",
        return_value=mock_tool_def,
    ):
        # THEN serialization should raise TriggerValidationError
        with pytest.raises(TriggerValidationError) as exc_info:
            workflow_display.serialize()

    # AND the error message should indicate the type mismatch with expected and actual types
    assert "action" in str(exc_info.value)
    assert "STRING" in str(exc_info.value)
    assert "expected type 'JSON'" in str(exc_info.value)
    assert "The trigger configuration is invalid or contains unsupported values" in str(exc_info.value)


def test_integration_trigger_validation__api_error():
    """
    Tests that serialization continues gracefully when the API returns an error.
    """
    # GIVEN an API that raises an exception
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integration_providers,
        "retrieve_integration_provider_tool_definition",
        side_effect=Exception("API Error"),
    ):
        # THEN serialization should succeed (validation is skipped on API error)
        result = workflow_display.serialize()

    # AND the trigger should still be serialized
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1


def test_integration_trigger_validation__no_output_parameters():
    """
    Tests that serialization continues gracefully when the API response has no output_parameters.
    """
    # GIVEN a tool definition with empty output_parameters
    mock_tool_def = _create_mock_tool_definition({})

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integration_providers,
        "retrieve_integration_provider_tool_definition",
        return_value=mock_tool_def,
    ):
        # THEN serialization should succeed (validation is skipped when no output_parameters)
        result = workflow_display.serialize()

    # AND the trigger should still be serialized
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
