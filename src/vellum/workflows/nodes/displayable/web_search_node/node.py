import logging
from typing import Any, ClassVar, Dict, List, Optional

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.core import ApiError
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.types.generics import StateType

logger = logging.getLogger(__name__)


class WebSearchResult(UniversalBaseModel):
    title: str
    url: str
    snippet: Optional[str] = None


class WebSearchNode(BaseNode[StateType]):
    """
    Used to perform web search using SerpAPI.

    query: str - The search query to execute
    """

    class Display(BaseNode.Display):
        icon = "vellum:icon:magnifying-glass"
        color = "lightBlue"

    query: ClassVar[str] = ""

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

    def _validate_query(self) -> str:
        if not self.query or not isinstance(self.query, str) or not self.query.strip():
            raise NodeException(
                "Query is required and must be a non-empty string", code=WorkflowErrorCode.INVALID_INPUTS
            )

        return self.query.strip()

    def run(self) -> Outputs:
        """Run the WebSearchNode to perform web search via SerpAPI."""
        query = self._validate_query()

        try:
            response = self._context.vellum_client.integrations.execute_integration_tool(
                integration_name="SERPAPI",
                integration_provider="COMPOSIO",
                tool_name="SERPAPI_SEARCH",
                arguments={"query": query},
            )
        except ApiError as e:
            if e.status_code == 403 and isinstance(e.body, dict):
                raise NodeException(
                    message=e.body.get("detail", "You must provide authenticate with the search provider."),
                    code=WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE,
                ) from e
            elif e.status_code == 404 and isinstance(e.body, dict):
                error_message = e.body.get("detail", "Tool not found")
                raise NodeException(message=error_message, code=WorkflowErrorCode.PROVIDER_ERROR) from e

            error_message = (
                e.body.get("detail", f"Failed to execute SerpAPI search: {str(e)}")
                if isinstance(e.body, dict)
                else f"Failed to execute SerpAPI search: {str(e)}"
            )
            raise NodeException(message=error_message, code=WorkflowErrorCode.INTERNAL_ERROR) from e

        web_search_results = self._parse_serpapi_results(response.data)
        return self._web_search_results_to_outputs(web_search_results)

    def _parse_serpapi_results(self, data: Dict) -> List[WebSearchResult]:
        if "error" in data:
            error_msg = data["error"]
            logger.error(f"SerpAPI returned error: {error_msg}")
            raise NodeException(f"SerpAPI error: {error_msg}", code=WorkflowErrorCode.PROVIDER_ERROR)

        try:
            results: Dict = data["results"]
            organic_results: List[Dict] = results["organic_results"]
        except KeyError as e:
            raise NodeException("Unable to parse web search response", code=WorkflowErrorCode.PROVIDER_ERROR) from e

        web_search_results: List[WebSearchResult] = []
        for result in organic_results:
            title = result["title"]
            url = result["link"]
            snippet = result.get("snippet")

            web_search_results.append(
                WebSearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                )
            )

        return web_search_results

    def _web_search_results_to_outputs(self, web_search_results: List[WebSearchResult]) -> Outputs:
        text: str = ""
        urls: List[str] = []
        results: List[Dict] = []

        for web_search_result in web_search_results:
            if text:
                text += "\n\n"

            text += f"Title: {web_search_result.title}"
            if web_search_result.snippet:
                text += f"\nSnippet: {web_search_result.snippet}"
            if web_search_result.url:
                text += f"\nURL: {web_search_result.url}"
                urls.append(web_search_result.url)

            results.append(web_search_result.model_dump(mode="json"))

        return self.Outputs(
            text=text,
            urls=urls,
            results=results,
        )
