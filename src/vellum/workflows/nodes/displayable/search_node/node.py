from typing import ClassVar

from vellum.workflows.nodes.displayable.bases import BaseSearchNode as BaseSearchNode
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType


class SearchNode(BaseSearchNode[StateType]):
    """
    Used to perform a hybrid search against a Document Index in Vellum.

    document_index: Union[UUID, str] - Either the UUID or name of the Vellum Document Index that you'd like to search
        against
    query: str - The query to search for
    options: Optional[SearchRequestOptionsRequest] = None - Runtime configuration for the search
    request_options: Optional[RequestOptions] = None - The request options to use for the search
    chunk_separator: str = "\n\n#####\n\n" - The separator to use when joining the text of each search result
    """

    chunk_separator: ClassVar[str] = "\n\n#####\n\n"

    class Trigger(BaseSearchNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Outputs(BaseSearchNode.Outputs):
        """
        The outputs of the SearchNode.

        results: List[SearchResult] - The raw search results
        text: str - The text of the search results joined by the chunk_separator
        """

        text: str

    def run(self) -> Outputs:
        results = self._perform_search().results
        text = self.chunk_separator.join([r.text for r in results])
        return self.Outputs(results=results, text=text)
