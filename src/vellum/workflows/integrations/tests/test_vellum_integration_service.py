import pytest
from unittest.mock import Mock, patch

from vellum.client.core.api_error import ApiError
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.integrations.vellum_integration_service import VellumIntegrationService


@pytest.fixture
def service_setup():
    vellum_client = Mock()
    integrations_client = Mock()
    vellum_client.integrations = integrations_client

    with patch(
        "vellum.workflows.integrations.vellum_integration_service.create_vellum_client", return_value=vellum_client
    ):
        service = VellumIntegrationService()

    return service, integrations_client


class TestVellumIntegrationService:
    def test_retrieve_integration_tool_definition_success(self, service_setup):
        service, integrations_client = service_setup
        response_payload = {"description": "desc", "parameters": {"type": "object"}}

        integrations_client.retrieve_integration_tool_definition.return_value = response_payload

        result = service.retrieve_integration_tool_definition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="github",
            name="create_issue",
        )

        assert result == response_payload
        integrations_client.retrieve_integration_tool_definition.assert_called_once_with(
            provider="COMPOSIO",
            integration="github",
            tool_name="create_issue",
        )

    def test_execute_integration_tool_success(self, service_setup):
        service, integrations_client = service_setup
        response_payload = {"successful": True, "data": {"result": "ok"}}

        integrations_client.execute_integration_tool.return_value = response_payload

        result = service.execute_integration_tool(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="github",
            name="create_issue",
            arguments={"title": "Bug"},
        )

        assert result == {"result": "ok"}
        integrations_client.execute_integration_tool.assert_called_once_with(
            provider="COMPOSIO",
            integration="github",
            tool_name="create_issue",
            arguments={"title": "Bug"},
        )

    def test_execute_integration_tool_failure_returns_error_message(self, service_setup):
        service, integrations_client = service_setup
        response_payload = {"successful": False, "error": "Detailed error"}

        integrations_client.execute_integration_tool.return_value = response_payload

        result = service.execute_integration_tool(
            provider="COMPOSIO",
            integration="github",
            name="create_issue",
            arguments={"title": "Bug"},
        )

        assert result == "Detailed error"

    def test_unauthorized_request_raises_node_exception(self, service_setup):
        service, integrations_client = service_setup
        integrations_client.execute_integration_tool.side_effect = ApiError(
            status_code=401,
            body="Unauthorized",
        )

        with pytest.raises(NodeException) as exc_info:
            service.execute_integration_tool(
                provider=VellumIntegrationProviderType.COMPOSIO,
                integration="github",
                name="create_issue",
                arguments={"title": "Bug"},
            )

        assert exc_info.value.code == WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE
