from typing import Any, Generic, TypeVar

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.types.core import JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext

from ee.vellum_ee.workflows.display.vellum import GenericNodeDisplayData

_BaseNodeType = TypeVar("_BaseNodeType", bound=BaseNode)


class BaseNodeDisplay(BaseNodeVellumDisplay[_BaseNodeType], Generic[_BaseNodeType]):
    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        node = self._node
        node_id = self.node_id

        return {
            "id": str(node_id),
            "type": "GENERIC",
            "display_data": self.get_display_data().dict(),
            "definition": self.get_definition().dict(),
            "ports": [],
            "trigger": {
                "id": str(uuid4_from_hash(f"{node_id}|trigger")),
                "merge_behavior": node.Trigger.merge_behavior.value,
            },
        }

    def get_display_data(self) -> GenericNodeDisplayData:
        explicit_value = self._get_explicit_node_display_attr("display_data", GenericNodeDisplayData)
        return explicit_value if explicit_value else GenericNodeDisplayData()
