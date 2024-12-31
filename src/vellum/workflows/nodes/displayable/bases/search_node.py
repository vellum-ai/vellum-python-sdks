from decimal import Decimal
from uuid import UUID
from typing import ClassVar, Generic, List, Optional, Union

from vellum import (
    NotFoundError,
    SearchFiltersRequest,
    SearchRequestOptionsRequest,
    SearchResponse,
    SearchResult,
    SearchResultMergingRequest,
    SearchWeightsRequest,
)
from vellum.core import ApiError, RequestOptions
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.types.generics import StateType

DEFAULT_SEARCH_WEIGHTS = 0.8
DEFAULT_SEARCH_LIMIT = 8


def get_default_results_merging() -> SearchResultMergingRequest:
    return SearchResultMergingRequest(enabled=True)


class BaseSearchNode(BaseNode[StateType], Generic[StateType]):
    """
    Used to perform a hybrid search against a Document Index in Vellum.

    document_index: Union[UUID, str] - Either the UUID or name of the Vellum Document Index that you'd like to search
        against
    query: str - The query to search for
    options: Optional[SearchRequestOptionsRequest] = None - Runtime configuration for the search
    request_options: Optional[RequestOptions] = None - The request options to use for the search
    """

    # The query to search for.
    query: ClassVar[str]

    # The Document Index to Search against. Identified by either its UUID or its name.
    document_index: ClassVar[Union[UUID, str]]

    # Ideally we could reuse node descriptors to derive other node descriptor values. Two action items are
    # blocking us from doing so in this use case:
    # 1. Node Descriptor resolution during runtime - https://app.shortcut.com/vellum/story/4781
    # 2. Math operations between descriptors - https://app.shortcut.com/vellum/story/4782
    # search_weights = DEFAULT_SEARCH_WEIGHTS
    options = SearchRequestOptionsRequest(
        limit=DEFAULT_SEARCH_LIMIT,
        weights=SearchWeightsRequest(
            semantic_similarity=DEFAULT_SEARCH_WEIGHTS,
            keywords=float(Decimal("1.0") - Decimal(str(DEFAULT_SEARCH_WEIGHTS))),
        ),
        result_merging=get_default_results_merging(),
        filters=SearchFiltersRequest(
            external_ids=None,
            metadata=None,
        ),
    )

    request_options: Optional[RequestOptions] = None

    class Outputs(BaseOutputs):
        """
        The outputs of the SearchNode.

        results: List[SearchResult] - The raw search results
        """

        results: List[SearchResult]

    def _perform_search(self) -> SearchResponse:
        try:
            return self._context.vellum_client.search(
                query=self.query,
                document_index=str(self.document_index),
                options=self.options,
            )
        except NotFoundError:
            raise NodeException(
                message=f"Document Index '{self.document_index}' not found",
                code=WorkflowErrorCode.INVALID_INPUTS,
            )
        except ApiError:
            raise NodeException(
                message=f"An error occurred while searching against Document Index '{self.document_index}'",  # noqa: E501
                code=WorkflowErrorCode.INTERNAL_ERROR,
            )

    def run(self) -> Outputs:
        response = self._perform_search()
        return self.Outputs(results=response.results)
