import pytest
from unittest.mock import MagicMock

import requests

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException

from ...engines.serpapi import SerpAPIEngine


@pytest.fixture
def vellum_context():
    """Mock WorkflowContext with vellum_client."""
    context = MagicMock()
    context.vellum_client._client_wrapper.get_headers.return_value = {"User-Agent": "vellum-python-sdk/1.0.0"}
    return context


@pytest.fixture
def serpapi_engine():
    """Create SerpAPIEngine instance."""
    return SerpAPIEngine()


def test_successful_search_with_results(serpapi_engine, vellum_context, requests_mock):
    """Test successful SerpAPI search with typical organic results."""
    # GIVEN a mock SerpAPI response with organic results
    mock_response = {
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

    requests_mock.get("https://serpapi.com/search", json=mock_response)

    # WHEN we search with the engine
    result = serpapi_engine.search(
        query="test query",
        api_key="test_api_key",
        num_results=3,
        location=None,
        context=vellum_context,
    )

    # THEN the text output should be properly formatted
    expected_text = (
        "First Result: This is the first search result snippet\n\n"
        "Second Result: This is the second search result snippet\n\n"
        "Third Result: This is the third search result snippet"
    )
    assert result["text"] == expected_text

    # AND URLs should be extracted correctly
    assert result["urls"] == ["https://example1.com", "https://example2.com", "https://example3.com"]

    # AND raw results should be preserved
    assert result["results"] == mock_response["organic_results"]

    # AND the request should have the correct parameters
    assert requests_mock.last_request.qs == {
        "q": ["test query"],
        "api_key": ["test_api_key"],
        "num": ["3"],
        "engine": ["google"],
    }


def test_search_with_location_parameter(serpapi_engine, vellum_context, requests_mock):
    """Test that location parameter is properly passed to SerpAPI."""
    # GIVEN a location parameter is set
    requests_mock.get("https://serpapi.com/search", json={"organic_results": []})

    # WHEN we search with location
    serpapi_engine.search(
        query="test query",
        api_key="test_api_key",
        num_results=10,
        location="New York, NY",
        context=vellum_context,
    )

    # THEN the location parameter should be included
    assert "location" in requests_mock.last_request.qs
    assert requests_mock.last_request.qs["location"][0].lower() == "new york, ny"


def test_authentication_error_401(serpapi_engine, vellum_context, requests_mock):
    """Test 401 authentication error raises NodeException with INVALID_INPUTS."""
    # GIVEN SerpAPI returns a 401 authentication error
    requests_mock.get("https://serpapi.com/search", status_code=401)

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        serpapi_engine.search(
            query="test query",
            api_key="invalid_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Invalid API key" in str(exc_info.value)


def test_rate_limit_error_429(serpapi_engine, vellum_context, requests_mock):
    """Test 429 rate limit error raises NodeException with PROVIDER_ERROR."""
    # GIVEN SerpAPI returns a 429 rate limit error
    requests_mock.get("https://serpapi.com/search", status_code=429)

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        serpapi_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Rate limit exceeded" in str(exc_info.value)


def test_server_error_500(serpapi_engine, vellum_context, requests_mock):
    """Test 500+ server errors raise NodeException with PROVIDER_ERROR."""
    # GIVEN SerpAPI returns a 500 server error
    requests_mock.get("https://serpapi.com/search", status_code=500)

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        serpapi_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "SerpAPI error: HTTP 500" in str(exc_info.value)


def test_invalid_json_response(serpapi_engine, vellum_context, requests_mock):
    """Test non-JSON response raises appropriate NodeException."""
    # GIVEN SerpAPI returns non-JSON content
    requests_mock.get("https://serpapi.com/search", text="Not JSON")

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        serpapi_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Invalid JSON response" in str(exc_info.value)


def test_serpapi_error_in_response(serpapi_engine, vellum_context, requests_mock):
    """Test SerpAPI error field in response raises NodeException."""
    # GIVEN SerpAPI returns an error in the response body
    requests_mock.get("https://serpapi.com/search", json={"error": "Invalid search parameters"})

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        serpapi_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Invalid search parameters" in str(exc_info.value)


def test_empty_organic_results(serpapi_engine, vellum_context, requests_mock):
    """Test handling of empty search results."""
    # GIVEN SerpAPI returns no organic results
    requests_mock.get("https://serpapi.com/search", json={"organic_results": []})

    # WHEN we search
    result = serpapi_engine.search(
        query="test query",
        api_key="test_key",
        num_results=10,
        location=None,
        context=vellum_context,
    )

    # THEN all outputs should be empty
    assert result["text"] == ""
    assert result["urls"] == []
    assert result["results"] == []


def test_missing_fields_in_results(serpapi_engine, vellum_context, requests_mock):
    """Test handling of missing title, snippet, or link fields."""
    # GIVEN SerpAPI returns results with missing fields
    mock_response = {
        "organic_results": [
            {
                "title": "Only Title",
                # Missing snippet and link
            },
            {
                "snippet": "Only snippet, no title or link"
                # Missing title and link
            },
            {
                "title": "Title with link",
                "link": "https://example.com",
                # Missing snippet
            },
            {
                # All fields missing - should be skipped
                "position": 4
            },
        ]
    }

    requests_mock.get("https://serpapi.com/search", json=mock_response)

    # WHEN we search
    result = serpapi_engine.search(
        query="test query",
        api_key="test_key",
        num_results=10,
        location=None,
        context=vellum_context,
    )

    # THEN text should handle missing fields gracefully
    expected_text = "Only Title\n\n" "Only snippet, no title or link\n\n" "Title with link"
    assert result["text"] == expected_text

    # AND URLs should only include valid links
    assert result["urls"] == ["https://example.com"]


def test_request_timeout_handling(serpapi_engine, vellum_context, requests_mock):
    """Test network timeout raises appropriate error."""
    # GIVEN a network timeout occurs
    requests_mock.get("https://serpapi.com/search", exc=requests.exceptions.Timeout("Connection timed out"))

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        serpapi_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise a provider error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "HTTP request failed" in str(exc_info.value)


def test_user_agent_header_included(serpapi_engine, vellum_context, requests_mock):
    """Test that User-Agent header from vellum_client is included."""
    # GIVEN a successful request
    requests_mock.get("https://serpapi.com/search", json={"organic_results": []})

    # WHEN we search
    serpapi_engine.search(
        query="test query",
        api_key="test_key",
        num_results=10,
        location=None,
        context=vellum_context,
    )

    # THEN the User-Agent header should be included
    assert requests_mock.last_request.headers["User-Agent"] == "vellum-python-sdk/1.0.0"
