import pytest
from unittest.mock import Mock, patch

from vellum.workflows.nodes.displayable.tool_calling_node.composio_service import ComposioService, ConnectionInfo


@pytest.fixture
def mock_requests():
    """Mock requests module"""
    with patch("vellum.workflows.nodes.displayable.tool_calling_node.composio_service.requests") as mock_requests:
        yield mock_requests


@pytest.fixture
def mock_connected_accounts_response():
    """Mock response for connected accounts API"""
    return {
        "items": [
            {
                "id": "conn-123",
                "toolkit": {"slug": "github"},
                "status": "ACTIVE",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-15T10:30:00Z",
            },
            {
                "id": "conn-456",
                "toolkit": {"slug": "slack"},
                "status": "ACTIVE",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-10T08:00:00Z",
            },
        ]
    }


@pytest.fixture
def mock_tool_execution_response():
    """Mock response for tool execution API"""
    return {
        "data": {"items": [], "total": 0},
        "successful": True,
        "error": None,
    }


@pytest.fixture
def composio_service():
    """Create ComposioService with test API key"""
    return ComposioService(api_key="test-key")


class TestComposioAccountService:
    """Test suite for ComposioAccountService"""

    def test_get_user_connections_success(self, composio_service, mock_requests, mock_connected_accounts_response):
        """Test successful retrieval of user connections"""
        # GIVEN the requests mock returns a valid response with two connections
        mock_response = Mock()
        mock_response.json.return_value = mock_connected_accounts_response
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

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

        # Verify the correct API endpoint was called
        mock_requests.get.assert_called_once_with(
            "https://backend.composio.dev/api/v3/connected_accounts",
            headers={"x-api-key": "test-key", "Content-Type": "application/json"},
            params={},
            timeout=30,
        )

    def test_get_user_connections_empty_response(self, composio_service, mock_requests):
        """Test handling of empty connections response"""
        # GIVEN the requests mock returns an empty response
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        # WHEN we request user connections
        result = composio_service.get_user_connections()

        # THEN we get an empty list
        assert result == []


class TestComposioCoreService:
    """Test suite for ComposioCoreService"""

    def test_execute_tool_success(self, composio_service, mock_requests, mock_tool_execution_response):
        """Test executing a tool with complex argument structure"""
        # GIVEN complex arguments and a mock response
        complex_args = {"filters": {"status": "active"}, "limit": 10, "sort": "created_at"}
        mock_response = Mock()
        mock_response.json.return_value = mock_tool_execution_response
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        # WHEN we execute a tool with complex arguments
        result = composio_service.execute_tool("HACKERNEWS_GET_USER", complex_args)

        # THEN the arguments are passed through correctly and we get the expected result
        mock_requests.post.assert_called_once_with(
            "https://backend.composio.dev/api/v3/tools/execute/HACKERNEWS_GET_USER",
            headers={"x-api-key": "test-key", "Content-Type": "application/json"},
            json={"arguments": complex_args},
            timeout=30,
        )
        assert result == {"items": [], "total": 0}
