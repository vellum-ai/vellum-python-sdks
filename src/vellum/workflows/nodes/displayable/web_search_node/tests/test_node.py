import pytest
from unittest.mock import MagicMock

from vellum.client.types.composio_execute_tool_response import ComposioExecuteToolResponse
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.state import BaseState
from vellum.workflows.state.base import StateMeta

from ..node import WebSearchNode


@pytest.fixture
def base_node_setup(vellum_client):
    """Basic node setup with required inputs."""

    class Inputs(BaseInputs):
        query: str

    class State(BaseState):
        pass

    class TestableWebSearchNode(WebSearchNode):
        query = Inputs.query

    state = State(meta=StateMeta(workflow_inputs=Inputs(query="test query")))
    context = MagicMock()
    context.vellum_client = vellum_client
    node = TestableWebSearchNode(state=state, context=context)
    return node


def test_successful_search_with_results(base_node_setup):
    """Test successful SerpAPI search with typical organic results."""
    # GIVEN a mock Composio SerpAPI response with organic results
    mock_response_data = {
        "organic_results": [
            {
                "title": "First Result",
                "snippet": "This is the first search result snippet",
                "link": "https://example1.com",
                "position": 1,
            },
            {
                "title": "Second Result",
                "snippet": "This is the second search result snippet",
                "link": "https://example2.com",
                "position": 2,
            },
            {
                "title": "Third Result",
                "snippet": "This is the third search result snippet",
                "link": "https://example3.com",
                "position": 3,
            },
        ]
    }

    mock_response = ComposioExecuteToolResponse(provider="COMPOSIO", data=mock_response_data)
    base_node_setup._context.vellum_client.integrations.execute_integration_tool = MagicMock(return_value=mock_response)

    # WHEN we run the node
    outputs = base_node_setup.run()

    # THEN the text output should be properly formatted
    expected_text = (
        "First Result: This is the first search result snippet\n\n"
        "Second Result: This is the second search result snippet\n\n"
        "Third Result: This is the third search result snippet"
    )
    assert outputs.text == expected_text

    # AND URLs should be extracted correctly
    assert outputs.urls == ["https://example1.com", "https://example2.com", "https://example3.com"]

    # AND raw results should be preserved
    assert outputs.results == mock_response_data["organic_results"]

    # AND the Vellum client should have been called with the correct parameters
    base_node_setup._context.vellum_client.integrations.execute_integration_tool.assert_called_once_with(
        integration_name="SERPAPI",
        integration_provider="COMPOSIO",
        tool_name="SERPAPI_SEARCH",
        arguments={"query": "test query"},
    )


def test_authentication_error_401(base_node_setup):
    """Test authentication error raises NodeException with PROVIDER_ERROR."""
    base_node_setup._context.vellum_client.integrations.execute_integration_tool = MagicMock(
        side_effect=Exception("Authentication failed")
    )

    # WHEN we run the node
    with pytest.raises(NodeException) as exc_info:
        base_node_setup.run()

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Failed to execute web search" in str(exc_info.value)


def test_serpapi_error_in_response(base_node_setup):
    """Test SerpAPI error field in response raises NodeException."""
    # GIVEN SerpAPI returns an error in the response data
    mock_response = ComposioExecuteToolResponse(provider="COMPOSIO", data={"error": "Invalid search parameters"})
    base_node_setup._context.vellum_client.integrations.execute_integration_tool = MagicMock(return_value=mock_response)

    # WHEN we run the node
    with pytest.raises(NodeException) as exc_info:
        base_node_setup.run()

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Invalid search parameters" in str(exc_info.value)


def test_empty_query_validation(vellum_client):
    """Test empty query raises validation error."""

    # GIVEN a node with an empty query
    class TestNode(WebSearchNode):
        query = ""

    context = MagicMock()
    context.vellum_client = vellum_client
    node = TestNode(state=BaseState(meta=StateMeta(workflow_inputs=BaseInputs())), context=context)

    # WHEN we run the node
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN it should raise a validation error
    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Query is required" in str(exc_info.value)


def test_empty_organic_results(base_node_setup):
    """Test handling of empty search results."""
    # GIVEN Composio SerpAPI returns no organic results
    mock_response = ComposioExecuteToolResponse(provider="COMPOSIO", data={"organic_results": []})
    base_node_setup._context.vellum_client.integrations.execute_integration_tool = MagicMock(return_value=mock_response)

    # WHEN we run the node
    outputs = base_node_setup.run()

    # THEN all outputs should be empty
    assert outputs.text == ""
    assert outputs.urls == []
    assert outputs.results == []


def test_missing_fields_in_results(base_node_setup):
    """Test handling of missing title, snippet, or link fields."""
    # GIVEN Composio SerpAPI returns results with missing fields
    mock_response_data = {
        "organic_results": [
            {
                "title": "Only Title",
            },
            {"snippet": "Only snippet, no title or link"},
            {
                "title": "Title with link",
                "link": "https://example.com",
            },
            {"position": 4},
        ]
    }

    mock_response = ComposioExecuteToolResponse(provider="COMPOSIO", data=mock_response_data)
    base_node_setup._context.vellum_client.integrations.execute_integration_tool = MagicMock(return_value=mock_response)

    # WHEN we run the node
    outputs = base_node_setup.run()

    # THEN text should handle missing fields gracefully
    expected_text = "Only Title\n\n" "Only snippet, no title or link\n\n" "Title with link"
    assert outputs.text == expected_text

    # AND URLs should only include valid links
    assert outputs.urls == ["https://example.com"]
