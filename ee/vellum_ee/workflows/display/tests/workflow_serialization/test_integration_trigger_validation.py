"""Tests for IntegrationTrigger attribute type validation during serialization."""

import pytest
from unittest.mock import MagicMock, patch
from typing import List

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


def _create_mock_tools_response(
    event_attributes: List[dict], trigger_name: str = "LINEAR_ISSUE_CREATED_TRIGGER"
) -> MagicMock:
    """Helper to create a mock tools response with event_attributes."""
    mock_tool = MagicMock()
    mock_tool.model_dump.return_value = {
        "provider": "COMPOSIO",
        "integration": {"id": "test-id", "provider": "COMPOSIO", "name": "LINEAR"},
        "name": trigger_name,
        "label": "Issue Created Trigger",
        "description": "Triggered when a new issue is created.",
        "event_attributes": event_attributes,
    }
    mock_response = MagicMock()
    mock_response.results = [mock_tool]
    return mock_response


def test_integration_trigger_validation__matching_types():
    """
    Tests that serialization succeeds when trigger attribute types match the API definition.
    """
    # GIVEN a tools response from the API with matching types
    mock_tools_response = _create_mock_tools_response(
        [
            {"key": "action", "type": "STRING"},
            {"key": "data", "type": "JSON"},
            {"key": "type", "type": "STRING"},
            {"key": "url", "type": "STRING"},
        ]
    )

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integration_providers,
        "list_integration_tools",
        return_value=mock_tools_response,
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
    # GIVEN a tools response from the API with mismatched types
    # The API says 'action' should be JSON, but our trigger defines it as STRING
    mock_tools_response = _create_mock_tools_response(
        [
            {"key": "action", "type": "JSON"},
            {"key": "data", "type": "JSON"},
            {"key": "type", "type": "STRING"},
            {"key": "url", "type": "STRING"},
        ]
    )

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integration_providers,
        "list_integration_tools",
        return_value=mock_tools_response,
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
        "list_integration_tools",
        side_effect=Exception("API Error"),
    ):
        # THEN serialization should succeed (validation is skipped on API error)
        result = workflow_display.serialize()

    # AND the trigger should still be serialized
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1


def test_integration_trigger_validation__no_event_attributes():
    """
    Tests that serialization continues gracefully when the API response has no event_attributes.
    """
    # GIVEN a tools response with empty event_attributes
    mock_tools_response = _create_mock_tools_response([])

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integration_providers,
        "list_integration_tools",
        return_value=mock_tools_response,
    ):
        # THEN serialization should succeed (validation is skipped when no event_attributes)
        result = workflow_display.serialize()

    # AND the trigger should still be serialized
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1


def test_integration_trigger_validation__trigger_not_found():
    """
    Tests that serialization continues gracefully when the trigger is not found in the API response.
    """
    # GIVEN a tools response that doesn't contain the trigger
    mock_tools_response = _create_mock_tools_response(
        [{"key": "action", "type": "STRING"}],
        trigger_name="DIFFERENT_TRIGGER",
    )

    # WHEN we serialize the workflow with mocked API
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    with patch.object(
        workflow_display._client.integration_providers,
        "list_integration_tools",
        return_value=mock_tools_response,
    ):
        # THEN serialization should succeed (validation is skipped when trigger not found)
        result = workflow_display.serialize()

    # AND the trigger should still be serialized
    assert "triggers" in result
    triggers = result["triggers"]
    assert isinstance(triggers, list)
    assert len(triggers) == 1
