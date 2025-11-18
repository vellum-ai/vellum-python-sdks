from typing import Generic, TypeVar

from vellum.workflows.nodes.displayable.tool_calling_node.utils import RouterNode
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay

_RouterNodeType = TypeVar("_RouterNodeType", bound=RouterNode)


class RouterNodeDisplay(BaseNodeDisplay[_RouterNodeType], Generic[_RouterNodeType]):
    display_data = NodeDisplayData(
        icon="vellum:icon:split",
        color="corn",
    )
