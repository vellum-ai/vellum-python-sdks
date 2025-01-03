from uuid import UUID
from typing import Any, ClassVar, Dict, Generic, Optional, TypeVar, cast

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.vellum import WorkspaceSecretPointer

_BaseNodeType = TypeVar("_BaseNodeType", bound=BaseNode)


class BaseNodeDisplay(BaseNodeVellumDisplay[_BaseNodeType], Generic[_BaseNodeType]):
    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs: Any
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        return {
            "id": str(node_id),
            "type": "GENERIC",
        }
