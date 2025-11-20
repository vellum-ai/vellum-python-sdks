from typing import Generic, TypeVar

from vellum.workflows.nodes.displayable.tool_calling_node.utils import FunctionNode
from vellum_ee.workflows.display.editor import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay

_FunctionNodeType = TypeVar("_FunctionNodeType", bound=FunctionNode)


class BaseFunctionNodeDisplay(BaseNodeDisplay[_FunctionNodeType], Generic[_FunctionNodeType]):
    """
    Display class for FunctionNode that sets the icon and color from FunctionNode.Display.
    """

    display_data = NodeDisplayData(icon="vellum:icon:rectangle-code", color="purple")
