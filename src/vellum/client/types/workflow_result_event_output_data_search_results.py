# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .workflow_node_result_event_state import WorkflowNodeResultEventState
import pydantic
from .search_result import SearchResult
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class WorkflowResultEventOutputDataSearchResults(UniversalBaseModel):
    """
    A Search Results output streamed from a Workflow execution.
    """

    id: typing.Optional[str] = None
    name: str
    state: WorkflowNodeResultEventState
    node_id: str
    delta: typing.Optional[str] = pydantic.Field(default=None)
    """
    The newly output string value. Only relevant for string outputs with a state of STREAMING.
    """

    type: typing.Literal["SEARCH_RESULTS"] = "SEARCH_RESULTS"
    value: typing.Optional[typing.List[SearchResult]] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow