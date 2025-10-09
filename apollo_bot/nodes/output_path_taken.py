from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .check_tag_node import CheckTagNode


class OutputPathTaken(TemplatingNode[BaseState, str]):
    """Templates the result indicating which path was taken."""

    template = """{% if is_tagged %}tagged{% else %}not_tagged{% endif %}"""
    inputs = {
        "is_tagged": CheckTagNode.Outputs.is_tagged,
    }
