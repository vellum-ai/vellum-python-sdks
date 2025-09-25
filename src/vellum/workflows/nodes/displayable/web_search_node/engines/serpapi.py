import logging
from typing import Any, Dict, Optional

from requests import Request, RequestException, Session
from requests.exceptions import JSONDecodeError

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException

from .base import SearchEngineBase

logger = logging.getLogger(__name__)


class SerpAPIEngine(SearchEngineBase):
    """
    SerpAPI search engine implementation.

    Uses Google search via SerpAPI service.
    """

    def search(
        self,
        query: str,
        api_key: str,
        num_results: int,
        location: Optional[str],
        context: Any,
    ) -> Dict[str, Any]:
        """Execute search via SerpAPI and return normalized response."""
        params = {
            "q": query,
            "api_key": api_key,
            "num": num_results,
            "engine": "google",
        }

        if location:
            params["location"] = location

        headers = {}
        client_headers = context.vellum_client._client_wrapper.get_headers()
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

        return self._normalize_response(json_response)

    def _normalize_response(self, json_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize SerpAPI response to standard format.

        Args:
            json_response: Raw SerpAPI response

        Returns:
            Normalized response with text, urls, and results fields
        """
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

        return {
            "text": "\n\n".join(text_results),
            "urls": urls,
            "results": organic_results,
        }
