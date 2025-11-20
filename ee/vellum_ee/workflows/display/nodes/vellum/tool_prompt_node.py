from typing import Generic, TypeVar

from vellum.workflows.nodes.displayable.tool_calling_node.utils import ToolPromptNode
from vellum_ee.workflows.display.editor import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay

_ToolPromptNodeType = TypeVar("_ToolPromptNodeType", bound=ToolPromptNode)


class BaseToolPromptNodeDisplay(BaseNodeDisplay[_ToolPromptNodeType], Generic[_ToolPromptNodeType]):
    """
    Display class for ToolPromptNode that sets the icon and color to match PROMPT nodes.
    """

    display_data = NodeDisplayData(icon="vellum:icon:text-size", color="navy")
