import inspect
from typing import Any, Generic, Tuple, Type, TypeVar, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
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

        serialized_node = super().serialize(
            display_context,
            adornment=adornment,
        )

        if serialized_node["type"] == "GENERIC":
            return serialized_node

        serialized_node_definition = serialized_node.get("definition")
        if isinstance(serialized_node_definition, dict):
            serialized_node_definition_module = serialized_node_definition.get("module")
            if isinstance(serialized_node_definition_module, list):
                serialized_node_definition_module.extend(
                    [
                        serialized_node_definition["name"],
                        ADORNMENT_MODULE_NAME,
                    ]
                )
                serialized_node_definition["name"] = node.__name__

        return serialized_node

    def get_node_output_display(self, output: OutputReference) -> Tuple[Type[BaseNode], NodeOutputDisplay]:
        inner_node = self._node.__wrapped_node__
        if not inner_node:
            return super().get_node_output_display(output)

        node_display_class = get_node_display_class(BaseNodeDisplay, inner_node)
        node_display = node_display_class()

        inner_output = getattr(inner_node.Outputs, output.name)
        return node_display.get_node_output_display(inner_output)
