import pytest
from unittest.mock import MagicMock

import requests

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException

from ...engines.brave import BraveEngine


@pytest.fixture
def vellum_context():
    """Mock WorkflowContext with vellum_client."""
    context = MagicMock()
    context.vellum_client._client_wrapper.get_headers.return_value = {"User-Agent": "vellum-python-sdk/1.0.0"}
    return context


@pytest.fixture
def brave_engine():
    """Create BraveEngine instance."""
    return BraveEngine()


def test_successful_search_with_results(brave_engine, vellum_context, requests_mock):
    """Test successful Brave API search with typical web results."""
    # GIVEN a mock Brave API response with web results
    mock_response = {
        "web": {
            "results": [
                {
                    "title": "First Result",
                    "description": "This is the first search result description",
                    "url": "https://example1.com",
                },
                {
                    "title": "Second Result",
                    "description": "This is the second search result description",
                    "url": "https://example2.com",
                },
                {
                    "title": "Third Result",
                    "description": "This is the third search result description",
                    "url": "https://example3.com",
                },
            ]
        }
    }

    requests_mock.get("https://api.search.brave.com/res/v1/web/search", json=mock_response)

    # WHEN we search with the engine
    result = brave_engine.search(
        query="test query",
        api_key="test_api_key",
        num_results=3,
        location=None,
        context=vellum_context,
    )

    # THEN the text output should be properly formatted
    expected_text = (
        "First Result: This is the first search result description\n\n"
        "Second Result: This is the second search result description\n\n"
        "Third Result: This is the third search result description"
    )
    assert result["text"] == expected_text

    # AND URLs should be extracted correctly
    assert result["urls"] == ["https://example1.com", "https://example2.com", "https://example3.com"]

    # AND results should be normalized to SerpAPI format
    expected_results = [
        {
            "title": "First Result",
            "snippet": "This is the first search result description",  # description → snippet
            "link": "https://example1.com",  # url → link
        },
        {
            "title": "Second Result",
            "snippet": "This is the second search result description",
            "link": "https://example2.com",
        },
        {
            "title": "Third Result",
            "snippet": "This is the third search result description",
            "link": "https://example3.com",
        },
    ]
    assert result["results"] == expected_results

    # AND the request should have the correct parameters
    assert requests_mock.last_request.qs == {
        "q": ["test query"],
        "count": ["3"],  # Brave uses "count" vs SerpAPI's "num"
    }


def test_search_with_location_parameter(brave_engine, vellum_context, requests_mock):
    """Test that location parameter is converted to country code for Brave API."""
    # GIVEN a location parameter is set
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", json={"web": {"results": []}})

    # WHEN we search with location
    brave_engine.search(
        query="test query",
        api_key="test_api_key",
        num_results=10,
        location="New York, NY",
        context=vellum_context,
    )

    # THEN the country parameter should be included (converted from location)
    assert "country" in requests_mock.last_request.qs
    assert requests_mock.last_request.qs["country"][0] == "us"


def test_header_authentication(brave_engine, vellum_context, requests_mock):
    """Test that Brave API uses header-based authentication."""
    # GIVEN a successful request
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", json={"web": {"results": []}})

    # WHEN we search
    brave_engine.search(
        query="test query",
        api_key="test_brave_key",
        num_results=10,
        location=None,
        context=vellum_context,
    )

    # THEN the X-Subscription-Token header should be set
    assert requests_mock.last_request.headers["X-Subscription-Token"] == "test_brave_key"
    # AND Accept headers should be set
    assert requests_mock.last_request.headers["Accept"] == "application/json"
    assert requests_mock.last_request.headers["Accept-Encoding"] == "gzip"


def test_authentication_error_401(brave_engine, vellum_context, requests_mock):
    """Test 401 authentication error raises NodeException with INVALID_INPUTS."""
    # GIVEN Brave API returns a 401 authentication error
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", status_code=401)

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        brave_engine.search(
            query="test query",
            api_key="invalid_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Invalid API key" in str(exc_info.value)


def test_rate_limit_error_429(brave_engine, vellum_context, requests_mock):
    """Test 429 rate limit error raises NodeException with PROVIDER_ERROR."""
    # GIVEN Brave API returns a 429 rate limit error
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", status_code=429)

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        brave_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Rate limit exceeded" in str(exc_info.value)


def test_server_error_500(brave_engine, vellum_context, requests_mock):
    """Test 500+ server errors raise NodeException with PROVIDER_ERROR."""
    # GIVEN Brave API returns a 500 server error
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", status_code=500)

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        brave_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Brave API error: HTTP 500" in str(exc_info.value)


def test_invalid_json_response(brave_engine, vellum_context, requests_mock):
    """Test non-JSON response raises appropriate NodeException."""
    # GIVEN Brave API returns non-JSON content
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", text="Not JSON")

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        brave_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Invalid JSON response from Brave API" in str(exc_info.value)


def test_brave_api_error_in_response(brave_engine, vellum_context, requests_mock):
    """Test Brave API error field in response raises NodeException."""
    # GIVEN Brave API returns an error in the response body
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", json={"error": "Invalid search parameters"})

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        brave_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise the appropriate error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "Invalid search parameters" in str(exc_info.value)


def test_empty_web_results(brave_engine, vellum_context, requests_mock):
    """Test handling of empty search results."""
    # GIVEN Brave API returns no web results
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", json={"web": {"results": []}})

    # WHEN we search
    result = brave_engine.search(
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


def test_missing_web_section(brave_engine, vellum_context, requests_mock):
    """Test handling when web section is missing from response."""
    # GIVEN Brave API returns response without web section
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", json={})

    # WHEN we search
    result = brave_engine.search(
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


def test_missing_fields_in_results(brave_engine, vellum_context, requests_mock):
    """Test handling of missing title, description, or url fields."""
    # GIVEN Brave API returns results with missing fields
    mock_response = {
        "web": {
            "results": [
                {
                    "title": "Only Title",
                    # Missing description and url
                },
                {
                    "description": "Only description, no title or url"
                    # Missing title and url
                },
                {
                    "title": "Title with URL",
                    "url": "https://example.com",
                    # Missing description
                },
                {
                    # All fields missing
                },
            ]
        }
    }

    requests_mock.get("https://api.search.brave.com/res/v1/web/search", json=mock_response)

    # WHEN we search
    result = brave_engine.search(
        query="test query",
        api_key="test_key",
        num_results=10,
        location=None,
        context=vellum_context,
    )

    # THEN text should handle missing fields gracefully
    expected_text = "Only Title\n\n" "Only description, no title or url\n\n" "Title with URL"
    assert result["text"] == expected_text

    # AND URLs should only include valid links
    assert result["urls"] == ["https://example.com"]

    # AND results should be normalized with empty values for missing fields
    expected_results = [
        {"title": "Only Title", "snippet": "", "link": ""},
        {"title": "", "snippet": "Only description, no title or url", "link": ""},
        {"title": "Title with URL", "snippet": "", "link": "https://example.com"},
        {"title": "", "snippet": "", "link": ""},
    ]
    assert result["results"] == expected_results


def test_request_timeout_handling(brave_engine, vellum_context, requests_mock):
    """Test network timeout raises appropriate error."""
    # GIVEN a network timeout occurs
    requests_mock.get(
        "https://api.search.brave.com/res/v1/web/search", exc=requests.exceptions.Timeout("Connection timed out")
    )

    # WHEN we search
    with pytest.raises(NodeException) as exc_info:
        brave_engine.search(
            query="test query",
            api_key="test_key",
            num_results=10,
            location=None,
            context=vellum_context,
        )

    # THEN it should raise a provider error
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_ERROR
    assert "HTTP request failed" in str(exc_info.value)


def test_user_agent_header_included(brave_engine, vellum_context, requests_mock):
    """Test that User-Agent header from vellum_client is included."""
    # GIVEN a successful request
    requests_mock.get("https://api.search.brave.com/res/v1/web/search", json={"web": {"results": []}})

    # WHEN we search
    brave_engine.search(
        query="test query",
        api_key="test_key",
        num_results=10,
        location=None,
        context=vellum_context,
    )

    # THEN the User-Agent header should be included
    assert requests_mock.last_request.headers["User-Agent"] == "vellum-python-sdk/1.0.0"
