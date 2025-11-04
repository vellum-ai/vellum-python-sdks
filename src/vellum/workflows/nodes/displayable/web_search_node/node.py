import logging
from typing import Any, ClassVar, Dict, List

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
    """

    __legacy_id__ = True
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

    def _validate(self) -> None:
        """Validate node inputs."""
        if not self.query or not isinstance(self.query, str) or not self.query.strip():
            raise NodeException(
                "Query is required and must be a non-empty string", code=WorkflowErrorCode.INVALID_INPUTS
            )

    def run(self) -> Outputs:
        """Run the WebSearchNode to perform web search via SerpAPI."""
        self._validate()

        try:
            response = self._context.vellum_client.integrations.execute_integration_tool(
                integration_name="SERPAPI",
                integration_provider="COMPOSIO",
                tool_name="SERPAPI_SEARCH",
                arguments={"query": self.query},
            )
        except Exception as e:
            logger.exception("Failed to execute Composio SerpAPI tool")
            raise NodeException(f"Failed to execute web search: {e}", code=WorkflowErrorCode.PROVIDER_ERROR) from e

        response_data = response.data

        if "error" in response_data:
            error_msg = response_data["error"]
            logger.error(f"SerpAPI returned error: {error_msg}")
            raise NodeException(f"SerpAPI error: {error_msg}", code=WorkflowErrorCode.PROVIDER_ERROR)

        organic_results_raw = response_data.get("organic_results", [])
        organic_results: List[Dict[str, Any]] = organic_results_raw if organic_results_raw is not None else []

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
