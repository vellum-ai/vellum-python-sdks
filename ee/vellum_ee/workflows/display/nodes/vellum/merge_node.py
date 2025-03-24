from uuid import UUID
from typing import Any, ClassVar, Generic, List, Optional, TypeVar

from vellum.workflows.nodes.displayable import MergeNode
from vellum.workflows.types.core import JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_MergeNodeType = TypeVar("_MergeNodeType", bound=MergeNode)


class BaseMergeNodeDisplay(BaseNodeVellumDisplay[_MergeNodeType], Generic[_MergeNodeType]):
    target_handle_ids: ClassVar[List[UUID]]

    def __init__(self):
        super().__init__()
        self._target_handle_iterator = 0

    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        node = self._node
        node_id = self.node_id

        merged_source_ports = [
            source_node_port
            for (source_node_port, target_node), _ in display_context.edge_displays.items()
            if target_node.__id__ == self.node_id
        ]

        target_handle_ids = self.get_target_handle_ids()

        if target_handle_ids is None:
            target_handle_ids = [
                uuid4_from_hash(f"{node_id}|target_handle|{source_node_port.node_class.__id__}")
                for source_node_port in merged_source_ports
            ]
        elif len(target_handle_ids) != len(merged_source_ports):
            raise ValueError("If you explicitly specify target_handle_ids, you must specify one for each incoming edge")

        return {
            "id": str(node_id),
            "type": "MERGE",
            "inputs": [],
            "data": {
                "label": self.label,
                "merge_strategy": node.Trigger.merge_behavior.value,
                "target_handles": [{"id": str(target_handle_id)} for target_handle_id in target_handle_ids],
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
        }

    def get_target_handle_ids(self) -> Optional[List[UUID]]:
        return self._get_explicit_node_display_attr("target_handle_ids", List[UUID])

    def get_target_handle_id_by_source_node_id(self, source_node_id: UUID) -> UUID:
        target_handle_ids = self.get_target_handle_ids()
        if target_handle_ids is None:
            return uuid4_from_hash(f"{self.node_id}|target_handle|{source_node_id}")

        # Edges call this method to know which handle to connect to
        # We use the order of the edges to determine the handle id. This is quite brittle to the order of the
        # edges matching the order of the Merge Node's data.target_handles attribute. We should look into a
        # longer term solution, or cutover Merge Nodes to Generic Nodes soon
        target_handle_id = target_handle_ids[self._target_handle_iterator]
        self._target_handle_iterator += 1
        if self._target_handle_iterator >= len(self.target_handle_ids):
            self._target_handle_iterator = 0
        return target_handle_id
