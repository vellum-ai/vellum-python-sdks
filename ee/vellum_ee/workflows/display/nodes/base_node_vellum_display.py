from uuid import UUID
from typing import ClassVar, Dict, Optional, Union

from vellum.workflows.nodes.utils import get_unadorned_node
from vellum.workflows.ports import Port
from vellum.workflows.types.generics import NodeType
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplay
from vellum_ee.workflows.display.vellum import NodeDisplayComment, NodeDisplayData


class BaseNodeVellumDisplay(BaseNodeDisplay[NodeType]):
    # Used to explicitly set display data for a node
    display_data: ClassVar[Optional[NodeDisplayData]] = None

    # Used to explicitly set the target handle id for a node
    target_handle_id: ClassVar[Optional[UUID]] = None

    # Used to explicitly set the node input ids by name for a node
    node_input_ids_by_name: ClassVar[Dict[str, Union[UUID, str]]] = {}

    def _get_node_display_uuid(self, attribute: str) -> UUID:
        explicit_value = self._get_explicit_node_display_attr(attribute, UUID)
        return explicit_value if explicit_value else uuid4_from_hash(f"{self.node_id}|{attribute}")

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

    def get_target_handle_id(self) -> UUID:
        return self._get_node_display_uuid("target_handle_id")

    def get_target_handle_id_by_source_node_id(self, source_node_id: UUID) -> UUID:
        """
        In the vast majority of cases, nodes will only have a single target handle and can be retrieved independently
        of the source node. However, in rare cases (such as legacy Merge nodes), this method can be overridden to
        account for the case of retrieving one amongst multiple target handles on a node.
        """

        return self.get_target_handle_id()

    def get_source_handle_id(self, port_displays: Dict[Port, PortDisplay]) -> UUID:
        unadorned_node = get_unadorned_node(self._node)
        default_port = unadorned_node.Ports.default

        default_port_display = port_displays[default_port]
        return default_port_display.id
