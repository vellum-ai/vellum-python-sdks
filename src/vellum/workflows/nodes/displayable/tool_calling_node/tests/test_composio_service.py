import pytest
from unittest.mock import Mock, patch

from vellum.workflows.integrations.composio_service import ComposioService, ConnectionInfo


@pytest.fixture
def mock_requests():
    """Mock requests module"""
    with patch("vellum.workflows.integrations.composio_service.requests") as mock_requests:
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
def mock_tool_execution_error_response():
    """Mock response for failed tool execution API"""
    return {
        "data": {},
        "successful": False,
        "error": (
            'Request failed error: `{"message":"Not Found",'
            '"documentation_url":"https://docs.github.com/rest/pulls/pulls#get-a-pull-request",'
            '"status":"404"}`'
        ),
        "log_id": "log_raE_fIWNcDPo",
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

    def test_execute_tool_with_user_id(self, composio_service, mock_requests, mock_tool_execution_response):
        """Test executing a tool with user_id parameter"""
        # GIVEN a user_id and tool arguments
        user_id = "test_user_123"
        tool_args = {"param1": "value1"}
        mock_response = Mock()
        mock_response.json.return_value = mock_tool_execution_response
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        # WHEN we execute a tool with user_id
        result = composio_service.execute_tool("TEST_TOOL", tool_args, user_id=user_id)

        # THEN the user_id should be included in the request payload
        mock_requests.post.assert_called_once_with(
            "https://backend.composio.dev/api/v3/tools/execute/TEST_TOOL",
            headers={"x-api-key": "test-key", "Content-Type": "application/json"},
            json={"arguments": tool_args, "user_id": user_id},
            timeout=30,
        )
        assert result == {"items": [], "total": 0}

    def test_execute_tool_without_user_id(self, composio_service, mock_requests, mock_tool_execution_response):
        """Test executing a tool without user_id parameter maintains backward compatibility"""
        # GIVEN tool arguments without user_id
        tool_args = {"param1": "value1"}
        mock_response = Mock()
        mock_response.json.return_value = mock_tool_execution_response
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        # WHEN we execute a tool without user_id
        result = composio_service.execute_tool("TEST_TOOL", tool_args)

        # THEN the user_id should NOT be included in the request payload
        mock_requests.post.assert_called_once_with(
            "https://backend.composio.dev/api/v3/tools/execute/TEST_TOOL",
            headers={"x-api-key": "test-key", "Content-Type": "application/json"},
            json={"arguments": tool_args},
            timeout=30,
        )
        assert result == {"items": [], "total": 0}

    def test_execute_tool_failure_surfaces_error(
        self, composio_service, mock_requests, mock_tool_execution_error_response
    ):
        """Test that tool execution failures surface detailed error information"""
        # GIVEN a mock response indicating tool execution failure
        mock_response = Mock()
        mock_response.json.return_value = mock_tool_execution_error_response
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        # WHEN we execute a tool that fails
        result = composio_service.execute_tool("GITHUB_GET_PR", {"repo": "test", "pr_number": 999})

        # THEN the result should contain the detailed error message from the API
        assert "Request failed error" in result
        assert "Not Found" in result

    def test_execute_tool_failure_with_generic_error_message(self, composio_service, mock_requests):
        """Test that tool execution failures with missing error field use generic message"""
        # GIVEN a mock response indicating tool execution failure without error field
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {},
            "successful": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        # WHEN we execute a tool that fails
        result = composio_service.execute_tool("TEST_TOOL", {"param": "value"})

        # THEN the result should contain the generic error message
        assert result == "Tool execution failed"
