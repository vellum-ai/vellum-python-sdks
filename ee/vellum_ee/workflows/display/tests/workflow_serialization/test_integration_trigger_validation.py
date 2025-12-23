"""Tests for IntegrationTrigger attribute type validation during serialization."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict

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


def _create_mock_tool_definition(properties: Dict[str, dict]) -> MagicMock:
    """Helper to create a mock tool definition with output_parameters as JSON Schema.

    For triggers, output_parameters contains the webhook payload schema,
    while input_parameters contains setup/config arguments.
    """
    mock_tool_def = MagicMock()
    mock_tool_def.name = "LINEAR_ISSUE_CREATED_TRIGGER"
    # output_parameters is a JSON Schema object containing the payload schema
    mock_tool_def.output_parameters = {
        "type": "object",
        "properties": properties,
        "required": list(properties.keys()),
    }
    return mock_tool_def


def test_integration_trigger_validation__matching_types():
    """
    Tests that serialization succeeds when trigger attribute types match the API definition.
    """
    # GIVEN a tool definition from the API with matching types (JSON Schema format)
    mock_tool_def = _create_mock_tool_definition(
        {
            "action": {"type": "string"},
            "data": {"type": "object"},
            "type": {"type": "string"},
            "url": {"type": "string"},
        }
    )

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integrations,
        "retrieve_integration_tool_definition",
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
    # GIVEN a tool definition from the API with mismatched types (JSON Schema format)
    # The API says 'action' should be object (JSON), but our trigger defines it as STRING
    mock_tool_def = _create_mock_tool_definition(
        {
            "action": {"type": "object"},
            "data": {"type": "object"},
            "type": {"type": "string"},
            "url": {"type": "string"},
        }
    )

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integrations,
        "retrieve_integration_tool_definition",
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
        workflow_display._client.integrations,
        "retrieve_integration_tool_definition",
        side_effect=Exception("API Error"),
    ):
        # WHEN we serialize the workflow
        # THEN serialization should succeed (validation is skipped on API error)
        result = workflow_display.serialize()

    # AND the trigger should still be serialized
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1


def test_integration_trigger_validation__no_properties():
    """
    Tests that serialization continues gracefully when the API response has no properties.
    """
    # GIVEN a tool definition with empty properties in JSON Schema
    mock_tool_def = _create_mock_tool_definition({})

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integrations,
        "retrieve_integration_tool_definition",
        return_value=mock_tool_def,
    ):
        # THEN serialization should succeed (validation is skipped when no output_parameters)
        result = workflow_display.serialize()

    # AND the trigger should still be serialized
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
