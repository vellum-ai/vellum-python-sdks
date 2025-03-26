from uuid import UUID
from typing import Any, ClassVar, Generic, Optional, TypeVar

from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.types.core import JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import to_kebab_case
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type

_FinalOutputNodeType = TypeVar("_FinalOutputNodeType", bound=FinalOutputNode)


class BaseFinalOutputNodeDisplay(BaseNodeVellumDisplay[_FinalOutputNodeType], Generic[_FinalOutputNodeType]):
    output_id: ClassVar[Optional[UUID]] = None
    output_name: ClassVar[Optional[str]] = None
    node_input_id: ClassVar[Optional[UUID]] = None

    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        node = self._node
        node_id = self.node_id

        node_input = create_node_input(
            node_id,
            "node_input",
            # Get the pointer that the Terminal Node's output is referencing
            node.Outputs.value.instance,
            display_context,
            self._get_node_input_id(),
        )
        inferred_type = infer_vellum_variable_type(node.Outputs.value)

        return {
            "id": str(node_id),
            "type": "TERMINAL",
            "data": {
                "label": self.label,
                "name": self._get_output_name(),
                "target_handle_id": str(self.get_target_handle_id()),
                "output_id": str(self._get_output_id()),
                "output_type": inferred_type,
                "node_input_id": str(node_input.id),
            },
            "inputs": [node_input.dict()],
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
            "outputs": [
                {
                    "id": str(self._get_output_id()),
                    "name": node.Outputs.value.name,
                    "type": inferred_type,
                    "value": self.serialize_value(display_context, node.Outputs.value.instance),
                }
            ],
        }

    def _get_output_id(self) -> UUID:
        explicit_value = self._get_explicit_node_display_attr("output_id", UUID)
        return explicit_value if explicit_value else uuid4_from_hash(f"{self.node_id}|output_id")

    def _get_output_name(self) -> str:
        explicit_value = self._get_explicit_node_display_attr("output_name", str)
        return explicit_value if explicit_value else to_kebab_case(self._node.__name__)

    def _get_node_input_id(self) -> UUID:
        explicit_value = self._get_explicit_node_display_attr("node_input_id", UUID)
        return explicit_value if explicit_value else uuid4_from_hash(f"{self.node_id}|node_input_id")
