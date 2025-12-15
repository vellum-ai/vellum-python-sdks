import warnings
from typing import Any, ClassVar, Dict, Generic, Optional, TypeVar, Union, cast

from vellum.workflows.nodes import NoteNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_NoteNodeType = TypeVar("_NoteNodeType", bound=NoteNode)


class BaseNoteNodeDisplay(BaseNodeDisplay[_NoteNodeType], Generic[_NoteNodeType]):
    # Deprecated: Define text and style on the node class instead. Will be removed in v2.0.0.
    text: ClassVar[str] = ""
    style: ClassVar[Union[Dict[str, Any], None]] = None

    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        del kwargs  # Unused parameters
        node_id = self.node_id
        node = self._node

        text = raise_if_descriptor(node.text) or ""
        style = cast(Optional[Dict[str, Any]], raise_if_descriptor(node.style)) or None

        if "text" in self.__class__.__dict__ or "style" in self.__class__.__dict__:
            warnings.warn(
                "Defining 'text' and 'style' on the display class is deprecated. "
                "Define them on the node class instead. Will be removed in v2.0.0.",
                DeprecationWarning,
                stacklevel=2,
            )

        return {
            "id": str(node_id),
            "type": "NOTE",
            "inputs": [],
            "data": {
                "label": self.label,
                "text": text,
                "style": style,
            },
            **self.serialize_generic_fields(display_context, exclude=["outputs"]),
        }
