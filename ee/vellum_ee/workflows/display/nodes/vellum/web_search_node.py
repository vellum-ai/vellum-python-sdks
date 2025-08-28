from typing import Generic, TypeVar

from vellum.workflows.nodes.displayable.web_search_node import WebSearchNode
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay

_WebSearchNodeType = TypeVar("_WebSearchNodeType", bound=WebSearchNode)


class BaseWebSearchNodeDisplay(BaseNodeDisplay[_WebSearchNodeType], Generic[_WebSearchNodeType]):
    pass
