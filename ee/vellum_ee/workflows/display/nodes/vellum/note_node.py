import json
from typing import Any, ClassVar, Dict, Generic, TypeVar, Union

from vellum.workflows.nodes import NoteNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_NoteNodeType = TypeVar("_NoteNodeType", bound=NoteNode)


class BaseNoteNodeDisplay(BaseNodeVellumDisplay[_NoteNodeType], Generic[_NoteNodeType]):
    text: ClassVar[str] = ""
    style: ClassVar[Union[Dict[str, Any], None]] = None

    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        node_id = self.node_id

        return {
            "id": str(node_id),
            "type": "NOTE",
            "inputs": [],
            "data": {
                "label": self.label,
                "text": self.text,
                "style": json.dumps(self.style) if self.style else None,
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
        }
