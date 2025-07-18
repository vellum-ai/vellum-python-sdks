import pytest
from unittest.mock import Mock, patch

from vellum.workflows.nodes.displayable.tool_calling_node.composio_service import (
    ComposioAccountService,
    ComposioService,
    ConnectionInfo,
    ConnectionStatus,
)


@pytest.fixture
def mock_composio_client():
    """Mock the Composio client completely"""
    with patch("vellum.workflows.nodes.displayable.tool_calling_node.composio_service.ComposioClient") as mock_composio:
        yield mock_composio.return_value


@pytest.fixture
def mock_connected_accounts_response():
    """Mock response for connected accounts"""
    mock_item1 = Mock()
    mock_item1.id = "conn-123"
    mock_item1.toolkit.slug = "github"
    mock_item1.status = "ACTIVE"
    mock_item1.created_at = "2023-01-01T00:00:00Z"
    mock_item1.updated_at = "2023-01-15T10:30:00Z"

    mock_item2 = Mock()
    mock_item2.id = "conn-456"
    mock_item2.toolkit.slug = "slack"
    mock_item2.status = "ACTIVE"
    mock_item2.created_at = "2023-01-01T00:00:00Z"
    mock_item2.updated_at = "2023-01-10T08:00:00Z"

    mock_response = Mock()
    mock_response.items = [mock_item1, mock_item2]

    return mock_response


@pytest.fixture
def composio_account_service(mock_composio_client):
    """Create ComposioAccountService with mocked client"""
    return ComposioAccountService(api_key="test-key")


@pytest.fixture
def composio_service(mock_composio_client):
    """Create ComposioService with mocked client"""
    return ComposioService(api_key="test-key")


class TestComposioAccountService:
    """Test suite for ComposioAccountService"""

    def test_init(self, mock_composio_client):
        """Test ComposioAccountService initialization"""
        # GIVEN
        api_key = "test-api-key"

        # WHEN
        service = ComposioAccountService(api_key=api_key)

        # THEN
        assert service._client == mock_composio_client

    def test_get_user_connections_success(
        self, composio_account_service, mock_composio_client, mock_connected_accounts_response
    ):
        """Test successful retrieval of user connections"""
        # GIVEN
        mock_composio_client.connected_accounts.list.return_value = mock_connected_accounts_response

        # WHEN
        result = composio_account_service.get_user_connections()

        # THEN
        assert len(result) == 2
        assert isinstance(result[0], ConnectionInfo)
        assert result[0].connection_id == "conn-123"
        assert result[0].integration_name == "github"
        assert result[0].status == ConnectionStatus.ACTIVE
        assert result[0].created_at == "2023-01-01T00:00:00Z"
        assert result[0].updated_at == "2023-01-15T10:30:00Z"

        assert result[1].connection_id == "conn-456"
        assert result[1].integration_name == "slack"
        assert result[1].status == ConnectionStatus.ACTIVE
        assert result[1].created_at == "2023-01-01T00:00:00Z"
        assert result[1].updated_at == "2023-01-10T08:00:00Z"

        mock_composio_client.connected_accounts.list.assert_called_once()

    def test_get_user_connections_empty_response(self, composio_account_service, mock_composio_client):
        """Test handling of empty connections response"""
        # GIVEN
        mock_response = Mock()
        mock_response.items = []
        mock_composio_client.connected_accounts.list.return_value = mock_response

        # WHEN
        result = composio_account_service.get_user_connections()

        # THEN
        assert result == []
