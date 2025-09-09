import logging
from typing import Any, Dict, Optional

from requests import Request, RequestException, Session
from requests.exceptions import JSONDecodeError

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException

from .base import SearchEngineBase

logger = logging.getLogger(__name__)


class BraveEngine(SearchEngineBase):
    """
    Brave Search API engine implementation.

    Uses Brave's independent search index.
    """

    def search(
        self,
        query: str,
        api_key: str,
        num_results: int,
        location: Optional[str],
        context: Any,
    ) -> Dict[str, Any]:
        """Execute search via Brave Search API and return normalized response."""
        params = {
            "q": query,
            "count": num_results,  # Brave uses "count" vs SerpAPI's "num"
        }

        # Convert location to country code for Brave API
        if location:
            params["country"] = self._location_to_country_code(location)

        # Brave uses header authentication vs SerpAPI's query param
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,  # Header-based auth
        }

        # Include Vellum User-Agent
        client_headers = context.vellum_client._client_wrapper.get_headers()
        headers["User-Agent"] = client_headers.get("User-Agent")

        try:
            prepped = Request(
                method="GET", url="https://api.search.brave.com/res/v1/web/search", params=params, headers=headers
            ).prepare()
        except Exception as e:
            logger.exception("Failed to prepare Brave API request")
            raise NodeException(f"Failed to prepare HTTP request: {e}", code=WorkflowErrorCode.PROVIDER_ERROR) from e

        try:
            with Session() as session:
                response = session.send(prepped, timeout=30)
        except RequestException as e:
            logger.exception("Brave API request failed")
            raise NodeException(f"HTTP request failed: {e}", code=WorkflowErrorCode.PROVIDER_ERROR) from e

        if response.status_code == 401:
            logger.error("Brave API authentication failed")
            raise NodeException("Invalid API key", code=WorkflowErrorCode.INVALID_INPUTS)
        elif response.status_code == 429:
            logger.warning("Brave API rate limit exceeded")
            raise NodeException("Rate limit exceeded", code=WorkflowErrorCode.PROVIDER_ERROR)
        elif response.status_code >= 400:
            logger.error(f"Brave API returned error status: {response.status_code}")
            raise NodeException(f"Brave API error: HTTP {response.status_code}", code=WorkflowErrorCode.PROVIDER_ERROR)

        try:
            json_response = response.json()
        except JSONDecodeError as e:
            logger.exception("Failed to parse Brave API response as JSON")
            raise NodeException(
                f"Invalid JSON response from Brave API: {e}", code=WorkflowErrorCode.PROVIDER_ERROR
            ) from e

        # Brave doesn't use an "error" field like SerpAPI, but check for API errors
        if "error" in json_response:
            error_msg = json_response["error"]
            logger.error(f"Brave API returned error: {error_msg}")
            raise NodeException(f"Brave API error: {error_msg}", code=WorkflowErrorCode.PROVIDER_ERROR)

        return self._normalize_brave_response(json_response)

    def _normalize_brave_response(self, json_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Brave API response to SerpAPI-compatible format.

        Args:
            json_response: Raw Brave API response

        Returns:
            Normalized response with text, urls, and results fields compatible with SerpAPI
        """
        # Brave API structure: {"web": {"results": [...]}}
        web_results = json_response.get("web", {}).get("results", [])

        text_results = []
        urls = []
        normalized_results = []

        for result in web_results:
            title = result.get("title", "")
            description = result.get("description", "")  # Brave uses "description" vs SerpAPI's "snippet"
            url = result.get("url", "")  # Brave uses "url" vs SerpAPI's "link"

            # Convert to SerpAPI format for consistency
            normalized_result = {
                "title": title,
                "snippet": description,  # Map description → snippet
                "link": url,  # Map url → link
            }

            normalized_results.append(normalized_result)

            # Build text output same as SerpAPI
            if title and description:
                text_results.append(f"{title}: {description}")
            elif title:
                text_results.append(title)
            elif description:
                text_results.append(description)

            if url:
                urls.append(url)

        return {
            "text": "\n\n".join(text_results),
            "urls": urls,
            "results": normalized_results,  # Return normalized format for consistency
        }

    def _location_to_country_code(self, location: str) -> str:
        """
        Convert location string to country code for Brave API.

        Args:
            location: Location string (e.g., "New York, NY", "United States")

        Returns:
            Country code (e.g., "us", "uk", "ca")
        """
        # Simple mapping - can be expanded based on requirements
        location_lower = location.lower().strip()

        # Check longer/more specific terms first to avoid false matches
        # Australia variations (check before US to avoid "us" in "australia")
        if any(term in location_lower for term in ["australia", "sydney", "melbourne"]):
            return "au"
        # Germany variations (check before US to avoid "us" in "deutschland")
        elif any(term in location_lower for term in ["germany", "deutschland", "berlin"]):
            return "de"
        # United States variations
        elif (
            any(term in location_lower for term in ["united states", "usa", "new york", "california", "texas"])
            or location_lower == "us"
        ):
            return "us"
        # United Kingdom variations
        elif any(term in location_lower for term in ["united kingdom", "uk", "england", "london"]):
            return "uk"
        # Canada variations
        elif any(term in location_lower for term in ["canada", "toronto", "vancouver"]):
            return "ca"
        # France variations
        elif any(term in location_lower for term in ["france", "paris"]):
            return "fr"
        # Default to US if unable to determine
        else:
            logger.warning(f"Unable to determine country code for location: {location}, defaulting to 'us'")
            return "us"
