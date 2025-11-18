from typing import Generic, TypeVar

from vellum.workflows.nodes.displayable.tool_calling_node.utils import FunctionNode
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay

_FunctionNodeType = TypeVar("_FunctionNodeType", bound=FunctionNode)


class FunctionNodeDisplay(BaseNodeDisplay[_FunctionNodeType], Generic[_FunctionNodeType]):
    display_data = NodeDisplayData(
        icon="vellum:icon:rectangle-code",
        color="purple",
    )
