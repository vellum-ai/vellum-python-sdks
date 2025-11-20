from typing import Generic, TypeVar

from vellum.workflows.nodes.displayable.tool_calling_node.utils import ToolPromptNode
from vellum_ee.workflows.display.editor import NodeDisplayData
from vellum_ee.workflows.display.nodes.vellum.inline_prompt_node import BaseInlinePromptNodeDisplay

_ToolPromptNodeType = TypeVar("_ToolPromptNodeType", bound=ToolPromptNode)


class BaseToolPromptNodeDisplay(BaseInlinePromptNodeDisplay[_ToolPromptNodeType], Generic[_ToolPromptNodeType]):
    """
    Display class for ToolPromptNode that sets the icon and color to match PROMPT nodes.
    """

    display_data = NodeDisplayData(icon="vellum:icon:text-size", color="navy")
