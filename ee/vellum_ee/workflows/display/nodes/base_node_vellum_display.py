from uuid import UUID
from typing import Dict

from vellum.workflows.nodes.utils import get_unadorned_node
from vellum.workflows.ports import Port
from vellum.workflows.types.generics import NodeType
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplay


class BaseNodeVellumDisplay(BaseNodeDisplay[NodeType]):

    def get_source_handle_id(self, port_displays: Dict[Port, PortDisplay]) -> UUID:
        unadorned_node = get_unadorned_node(self._node)
        default_port = unadorned_node.Ports.default

        default_port_display = port_displays[default_port]
        return default_port_display.id
