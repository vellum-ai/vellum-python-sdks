from uuid import UUID
from typing import ClassVar, Dict, Optional

from vellum.workflows.nodes.utils import get_unadorned_node
from vellum.workflows.ports import Port
from vellum.workflows.types.generics import NodeType
from vellum_ee.workflows.display.editor.types import NodeDisplayComment, NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplay


class BaseNodeVellumDisplay(BaseNodeDisplay[NodeType]):
    # Used to explicitly set display data for a node
    display_data: ClassVar[Optional[NodeDisplayData]] = None

    def get_display_data(self) -> NodeDisplayData:
        explicit_value = self._get_explicit_node_display_attr("display_data", NodeDisplayData)
        docstring = self._node.__doc__

        if explicit_value and explicit_value.comment and docstring:
            comment = (
                NodeDisplayComment(value=docstring, expanded=explicit_value.comment.expanded)
                if explicit_value.comment.expanded
                else NodeDisplayComment(value=docstring)
            )
            return NodeDisplayData(
                position=explicit_value.position,
                width=explicit_value.width,
                height=explicit_value.height,
                comment=comment,
            )

        return explicit_value if explicit_value else NodeDisplayData()

    def get_source_handle_id(self, port_displays: Dict[Port, PortDisplay]) -> UUID:
        unadorned_node = get_unadorned_node(self._node)
        default_port = unadorned_node.Ports.default

        default_port_display = port_displays[default_port]
        return default_port_display.id
