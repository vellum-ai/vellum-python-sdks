import inspect
from typing import Any, Generic, TypeVar, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.vellum.base_adornment_node import BaseAdornmentNodeDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_RetryNodeType = TypeVar("_RetryNodeType", bound=RetryNode)


class BaseRetryNodeDisplay(BaseAdornmentNodeDisplay[_RetryNodeType], Generic[_RetryNodeType]):
    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        node = self._node
        node_id = self.node_id

        attributes: JsonArray = []
        for attribute in node:
            if inspect.isclass(attribute.instance) and issubclass(attribute.instance, BaseWorkflow):
                # We don't need to serialize attributes that are workflows
                continue

            id = str(uuid4_from_hash(f"{node_id}|{attribute.name}"))
            attributes.append(
                {
                    "id": id,
                    "name": attribute.name,
                    "value": self.serialize_value(display_context, cast(BaseDescriptor, attribute.instance)),
                }
            )

        adornment: JsonObject = {
            "id": str(node_id),
            "label": node.__qualname__,
            "base": self.get_base().dict(),
            "attributes": attributes,
        }

        return super().serialize(display_context, adornment=adornment)
