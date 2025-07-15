from unittest.mock import Mock, patch

from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.nodes.displayable.bases.api_node.node import BaseAPINode
from vellum.workflows.types.core import VellumSecret


class TestAPINodeTimeout:
    """Test timeout functionality in BaseAPINode."""

    def _setup_vellum_mocks(self, node):
        """Helper method to set up common vellum client mocks."""
        mock_context = Mock()
        mock_vellum_client = Mock()
        mock_vellum_response = Mock()
        mock_vellum_response.json_ = {"result": "success"}
        mock_vellum_response.headers = {"content-type": "application/json"}
        mock_vellum_response.status_code = 200
        mock_vellum_response.text = '{"result": "success"}'
        mock_vellum_client.execute_api.return_value = mock_vellum_response
        mock_context.vellum_client = mock_vellum_client
        node._context = mock_context
        return mock_vellum_client, mock_vellum_response

    @patch("vellum.workflows.nodes.displayable.bases.api_node.node.Session")
    def test_local_execute_api_with_timeout(self, mock_session):
        """Test that timeout is passed to local requests session."""
        mock_session_instance = Mock()
        mock_session.return_value.__enter__.return_value = mock_session_instance

        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.status_code = 200
        mock_response.text = '{"result": "success"}'
        mock_session_instance.send.return_value = mock_response

        node: BaseAPINode = BaseAPINode()
        node.url = "https://example.com"

        result = node._local_execute_api(
            data=None,
            headers={},
            json={"test": "data"},
            method=APIRequestMethod.POST,
            url="https://example.com",
            timeout=30,
        )

        # Verify timeout was passed to session.send
        mock_session_instance.send.assert_called_once()
        call_args = mock_session_instance.send.call_args
        assert call_args[1]["timeout"] == 30

        assert result.json == {"result": "success"}
        assert result.status_code == 200

    def test_vellum_execute_api_with_timeout(self):
        """Test that timeout creates RequestOptions for vellum client."""
        node: BaseAPINode = BaseAPINode()
        mock_vellum_client, mock_vellum_response = self._setup_vellum_mocks(node)

        result = node._vellum_execute_api(
            bearer_token=None,
            data={"test": "data"},
            headers={},
            method=APIRequestMethod.POST,
            url="https://example.com",
            timeout=45,
        )

        # Verify RequestOptions with timeout was passed
        mock_vellum_client.execute_api.assert_called_once()
        call_args = mock_vellum_client.execute_api.call_args
        request_options = call_args[1]["request_options"]
        assert request_options is not None
        assert request_options["timeout_in_seconds"] == 45

        assert result.json == {"result": "success"}
        assert result.status_code == 200

    def test_vellum_execute_api_with_bearer_token_and_timeout(self):
        """Test that timeout works with bearer token authentication."""
        node: BaseAPINode = BaseAPINode()
        mock_vellum_client, _ = self._setup_vellum_mocks(node)

        bearer_token = VellumSecret(name="test_token")

        node._vellum_execute_api(
            bearer_token=bearer_token,
            data={"test": "data"},
            headers={},
            method=APIRequestMethod.POST,
            url="https://example.com",
            timeout=60,
        )

        # Verify RequestOptions with timeout was passed
        mock_vellum_client.execute_api.assert_called_once()
        call_args = mock_vellum_client.execute_api.call_args
        request_options = call_args[1]["request_options"]
        assert request_options is not None
        assert request_options["timeout_in_seconds"] == 60

        # Verify bearer token was also passed
        bearer_token_arg = call_args[1]["bearer_token"]
        assert bearer_token_arg is not None
        assert bearer_token_arg.name == "test_token"

    def test_run_method_passes_timeout(self):
        """Test that the run() method properly passes timeout to _run()."""
        node: BaseAPINode = BaseAPINode()
        node.url = "https://example.com"
        node.method = APIRequestMethod.GET
        node.timeout = 25

        # Mock the _run method to verify timeout is passed
        with patch.object(node, "_run") as mock_run:
            mock_run.return_value = Mock()

            node.run()

            # Verify _run was called with timeout
            mock_run.assert_called_once_with(
                method=APIRequestMethod.GET, url="https://example.com", data=None, json=None, headers=None, timeout=25
            )
