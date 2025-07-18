import pytest
from unittest.mock import Mock, patch

from vellum.workflows.nodes.displayable.tool_calling_node.composio_service import ComposioService, ConnectionInfo


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
def mock_composio_core_client():
    """Mock the composio-core Composio client"""
    with patch("vellum.workflows.nodes.displayable.tool_calling_node.composio_service.Composio") as mock_composio:
        yield mock_composio.return_value


@pytest.fixture
def mock_action():
    """Mock the Action class and specific actions"""
    with patch("vellum.workflows.nodes.displayable.tool_calling_node.composio_service.Action") as mock_action_class:
        # Mock a specific action
        mock_hackernews_action = Mock()
        mock_action_class.HACKERNEWS_GET_USER = mock_hackernews_action
        mock_action_class.GITHUB_GET_USER = Mock()
        yield mock_action_class


@pytest.fixture
def composio_service(mock_composio_client, mock_composio_core_client):
    """Create ComposioService with mocked clients"""
    return ComposioService(api_key="test-key")


class TestComposioAccountService:
    """Test suite for ComposioAccountService"""

    def test_get_user_connections_success(
        self, composio_service, mock_composio_client, mock_connected_accounts_response
    ):
        """Test successful retrieval of user connections"""
        # GIVEN the Composio client returns a valid response with two connections
        mock_composio_client.connected_accounts.list.return_value = mock_connected_accounts_response

        # WHEN we request user connections
        result = composio_service.get_user_connections()

        # THEN we get two properly formatted ConnectionInfo objects
        assert len(result) == 2
        assert isinstance(result[0], ConnectionInfo)
        assert result[0].connection_id == "conn-123"
        assert result[0].integration_name == "github"
        assert result[0].status == "ACTIVE"
        assert result[0].created_at == "2023-01-01T00:00:00Z"
        assert result[0].updated_at == "2023-01-15T10:30:00Z"

        assert result[1].connection_id == "conn-456"
        assert result[1].integration_name == "slack"
        assert result[1].status == "ACTIVE"
        assert result[1].created_at == "2023-01-01T00:00:00Z"
        assert result[1].updated_at == "2023-01-10T08:00:00Z"

        mock_composio_client.connected_accounts.list.assert_called_once()

    def test_get_user_connections_empty_response(self, composio_service, mock_composio_client):
        """Test handling of empty connections response"""
        # GIVEN the Composio client returns an empty response
        mock_response = Mock()
        mock_response.items = []
        mock_composio_client.connected_accounts.list.return_value = mock_response

        # WHEN we request user connections
        result = composio_service.get_user_connections()

        # THEN we get an empty list
        assert result == []


class TestComposioCoreService:
    """Test suite for ComposioCoreService"""

    def test_execute_tool_success(self, composio_service, mock_composio_core_client, mock_action):
        """Test executing a tool with complex argument structure"""
        # GIVEN complex arguments and a mock response
        complex_args = {"filters": {"status": "active"}, "limit": 10, "sort": "created_at"}
        expected_result = {"items": [], "total": 0}
        mock_composio_core_client.actions.execute.return_value = expected_result

        # WHEN we execute a tool with complex arguments
        result = composio_service.execute_tool("HACKERNEWS_GET_USER", complex_args)

        # THEN the arguments are passed through correctly
        mock_composio_core_client.actions.execute.assert_called_once_with(
            mock_action.HACKERNEWS_GET_USER, params=complex_args
        )
        assert result == expected_result
