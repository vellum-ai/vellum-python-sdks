import logging
from typing import Any, ClassVar, Dict, List, Optional

from requests import Request, RequestException, Session
from requests.exceptions import JSONDecodeError

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.types.generics import StateType

logger = logging.getLogger(__name__)


class WebSearchNode(BaseNode[StateType]):
    """
    Used to perform web search using SerpAPI.

    query: str - The search query to execute
    api_key: str - SerpAPI authentication key
    num_results: int - Number of search results to return (default: 10)
    location: Optional[str] - Geographic location filter for search
    """

    query: ClassVar[str] = ""
    api_key: ClassVar[Optional[str]] = None
    num_results: ClassVar[int] = 10
    location: ClassVar[Optional[str]] = None

    class Outputs(BaseOutputs):
        """
        The outputs of the WebSearchNode.

        text: str - Concatenated search result snippets with titles
        urls: List[str] - List of URLs from search results
        results: List[Dict[str, Any]] - Raw search results from SerpAPI
        """

        text: str
        urls: List[str]
        results: List[Dict[str, Any]]

    def _validate(self) -> None:
        """Validate node inputs."""
        if not self.query or not isinstance(self.query, str) or not self.query.strip():
            raise NodeException(
                "Query is required and must be a non-empty string", code=WorkflowErrorCode.INVALID_INPUTS
            )

        if self.api_key is None:
            raise NodeException("API key is required", code=WorkflowErrorCode.INVALID_INPUTS)

        if not isinstance(self.num_results, int) or self.num_results <= 0:
            raise NodeException("num_results must be a positive integer", code=WorkflowErrorCode.INVALID_INPUTS)

    def run(self) -> Outputs:
        """Run the WebSearchNode to perform web search via SerpAPI."""
        self._validate()

        api_key_value = self.api_key

        params = {
            "q": self.query,
            "api_key": api_key_value,
            "num": self.num_results,
            "engine": "google",
        }

        if self.location:
            params["location"] = self.location

        headers = {}
        client_headers = self._context.vellum_client._client_wrapper.get_headers()
        headers["User-Agent"] = client_headers.get("User-Agent")

        try:
            prepped = Request(method="GET", url="https://serpapi.com/search", params=params, headers=headers).prepare()
        except Exception as e:
            logger.exception("Failed to prepare SerpAPI request")
            raise NodeException(f"Failed to prepare HTTP request: {e}", code=WorkflowErrorCode.PROVIDER_ERROR) from e

        try:
            with Session() as session:
                response = session.send(prepped, timeout=30)
        except RequestException as e:
            logger.exception("SerpAPI request failed")
            raise NodeException(f"HTTP request failed: {e}", code=WorkflowErrorCode.PROVIDER_ERROR) from e

        if response.status_code == 401:
            logger.error("SerpAPI authentication failed")
            raise NodeException("Invalid API key", code=WorkflowErrorCode.INVALID_INPUTS)
        elif response.status_code == 429:
            logger.warning("SerpAPI rate limit exceeded")
            raise NodeException("Rate limit exceeded", code=WorkflowErrorCode.PROVIDER_ERROR)
        elif response.status_code >= 400:
            logger.error(f"SerpAPI returned error status: {response.status_code}")
            raise NodeException(f"SerpAPI error: HTTP {response.status_code}", code=WorkflowErrorCode.PROVIDER_ERROR)

        try:
            json_response = response.json()
        except JSONDecodeError as e:
            logger.exception("Failed to parse SerpAPI response as JSON")
            raise NodeException(
                f"Invalid JSON response from SerpAPI: {e}", code=WorkflowErrorCode.PROVIDER_ERROR
            ) from e

        if "error" in json_response:
            error_msg = json_response["error"]
            logger.error(f"SerpAPI returned error: {error_msg}")
            raise NodeException(f"SerpAPI error: {error_msg}", code=WorkflowErrorCode.PROVIDER_ERROR)

        organic_results = json_response.get("organic_results", [])

        text_results = []
        urls = []

        for result in organic_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")

            if title and snippet:
                text_results.append(f"{title}: {snippet}")
            elif title:
                text_results.append(title)
            elif snippet:
                text_results.append(snippet)

            if link:
                urls.append(link)

        return self.Outputs(text="\n\n".join(text_results), urls=urls, results=organic_results)
