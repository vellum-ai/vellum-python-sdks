import inspect
from uuid import UUID
from typing import Any, Generic, Optional, TypeVar, cast

from vellum.workflows.constants import UNDEF
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.utils import get_wrapped_node
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.utils.vellum_variables import primitive_type_to_vellum_variable_type
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.vellum import GenericNodeDisplayData

_BaseNodeType = TypeVar("_BaseNodeType", bound=BaseNode)


class BaseNodeDisplay(BaseNodeVellumDisplay[_BaseNodeType], Generic[_BaseNodeType]):
    def serialize(
        self, display_context: WorkflowDisplayContext, adornments: Optional[JsonArray] = None, **kwargs: Any
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        attributes: JsonArray = []
        for attribute in node:
            if inspect.isclass(attribute.instance) and issubclass(attribute.instance, BaseWorkflow):
                # We don't need to serialize generic node attributes containing a subworkflow
                continue

            id = str(uuid4_from_hash(f"{node_id}|{attribute.name}"))
            attributes.append(
                {
                    "id": id,
                    "name": attribute.name,
                    "value": self.serialize_value(display_context, cast(BaseDescriptor, attribute.instance)),
                }
            )

        wrapped_node = get_wrapped_node(node)
        if wrapped_node is not None:
            display_class = get_node_display_class(BaseNodeDisplay, wrapped_node)

            adornment: JsonObject = {
                "id": str(node_id),
                "label": node.__qualname__,
                "base": self.get_base().dict(),
                "attributes": attributes,
            }

            existing_adornments = adornments if adornments is not None else []
            return display_class().serialize(display_context, adornments=existing_adornments + [adornment])

        ports: JsonArray = []
        for port in node.Ports:
            id = str(self.get_node_port_display(port).id)

            if port._condition_type:
                ports.append(
                    {
                        "id": id,
                        "name": port.name,
                        "type": port._condition_type.value,
                        "expression": (
                            self.serialize_condition(display_context, port._condition) if port._condition else None
                        ),
                    }
                )
            else:
                ports.append(
                    {
                        "id": id,
                        "name": port.name,
                        "type": "DEFAULT",
                    }
                )

        outputs: JsonArray = []
        for output in node.Outputs:
            type = primitive_type_to_vellum_variable_type(output)
            value = (
                self.serialize_value(display_context, output.instance)
                if output.instance is not None and output.instance != UNDEF
                else None
            )

            outputs.append(
                {
                    "id": str(uuid4_from_hash(f"{node_id}|{output.name}")),
                    "name": output.name,
                    "type": type,
                    "value": value,
                }
            )

        return {
            "id": str(node_id),
            "label": node.__qualname__,
            "type": "GENERIC",
            "display_data": self.get_generic_node_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
            "trigger": {
                "id": str(self.get_trigger_id()),
                "merge_behavior": node.Trigger.merge_behavior.value,
            },
            "ports": ports,
            "adornments": adornments,
            "attributes": attributes,
            "outputs": outputs,
        }

    def get_target_handle_id(self) -> UUID:
        return self.get_trigger_id()

    def get_generic_node_display_data(self) -> GenericNodeDisplayData:
        explicit_value = self._get_explicit_node_display_attr("display_data", GenericNodeDisplayData)
        return explicit_value if explicit_value else GenericNodeDisplayData()
