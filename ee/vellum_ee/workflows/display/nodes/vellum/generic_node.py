import inspect
from typing import Any, Generic, Optional, TypeVar, cast

from vellum.workflows.constants import UNDEF
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.expressions.between import BetweenExpression
from vellum.workflows.expressions.is_nil import IsNilExpression
from vellum.workflows.expressions.is_not_nil import IsNotNilExpression
from vellum.workflows.expressions.is_not_null import IsNotNullExpression
from vellum.workflows.expressions.is_not_undefined import IsNotUndefinedExpression
from vellum.workflows.expressions.is_null import IsNullExpression
from vellum.workflows.expressions.is_undefined import IsUndefinedExpression
from vellum.workflows.expressions.not_between import NotBetweenExpression
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.utils import get_wrapped_node
from vellum.workflows.references.execution_count import ExecutionCountReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.references.workflow_input import WorkflowInputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.utils.vellum_variables import primitive_type_to_vellum_variable_type
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.vellum.utils import convert_descriptor_to_operator
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import primitive_to_vellum_value
from vellum_ee.workflows.display.vellum import GenericNodeDisplayData

_BaseNodeType = TypeVar("_BaseNodeType", bound=BaseNode)


class GenericNodeDisplay(BaseNodeVellumDisplay[_BaseNodeType], Generic[_BaseNodeType]):
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
            display_class = get_node_display_class(GenericNodeDisplay, wrapped_node)

            adornment: JsonObject = {
                "id": str(node_id),
                "label": node.__qualname__,
                "base": self.get_base().dict(),
                "attributes": attributes,
            }

            existing_adornments = adornments if adornments is not None else []
            return display_class().serialize(display_context, adornments=existing_adornments + [adornment])

        ports: JsonArray = []
        for idx, port in enumerate(node.Ports):
            id = str(uuid4_from_hash(f"{node_id}|{idx}"))

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
                "id": str(uuid4_from_hash(f"{node_id}|trigger")),
                "merge_behavior": node.Trigger.merge_behavior.value,
            },
            "ports": ports,
            "adornments": adornments,
            "attributes": attributes,
            "outputs": outputs,
        }

    def get_generic_node_display_data(self) -> GenericNodeDisplayData:
        explicit_value = self._get_explicit_node_display_attr("display_data", GenericNodeDisplayData)
        return explicit_value if explicit_value else GenericNodeDisplayData()

    def serialize_condition(self, display_context: WorkflowDisplayContext, condition: BaseDescriptor) -> JsonObject:
        if isinstance(
            condition,
            (
                IsNullExpression,
                IsNotNullExpression,
                IsNilExpression,
                IsNotNilExpression,
                IsUndefinedExpression,
                IsNotUndefinedExpression,
            ),
        ):
            lhs = self.serialize_value(display_context, condition._expression)
            return {
                "type": "UNARY_EXPRESSION",
                "lhs": lhs,
                "operator": convert_descriptor_to_operator(condition),
            }
        elif isinstance(condition, (BetweenExpression, NotBetweenExpression)):
            base = self.serialize_value(display_context, condition._value)
            lhs = self.serialize_value(display_context, condition._start)
            rhs = self.serialize_value(display_context, condition._end)

            return {
                "type": "TERNARY_EXPRESSION",
                "base": base,
                "operator": convert_descriptor_to_operator(condition),
                "lhs": lhs,
                "rhs": rhs,
            }
        else:
            lhs = self.serialize_value(display_context, condition._lhs)  # type: ignore[attr-defined]
            rhs = self.serialize_value(display_context, condition._rhs)  # type: ignore[attr-defined]

            return {
                "type": "BINARY_EXPRESSION",
                "lhs": lhs,
                "operator": convert_descriptor_to_operator(condition),
                "rhs": rhs,
            }

    def serialize_value(self, display_context: WorkflowDisplayContext, value: BaseDescriptor) -> JsonObject:
        if isinstance(value, WorkflowInputReference):
            workflow_input_display = display_context.global_workflow_input_displays[value]
            return {
                "type": "WORKFLOW_INPUT",
                "input_variable_id": str(workflow_input_display.id),
            }

        if isinstance(value, OutputReference):
            upstream_node, output_display = display_context.global_node_output_displays[value]
            upstream_node_display = display_context.global_node_displays[upstream_node]

            return {
                "type": "NODE_OUTPUT",
                "node_id": str(upstream_node_display.node_id),
                "node_output_id": str(output_display.id),
            }

        if isinstance(value, VellumSecretReference):
            return {
                "type": "VELLUM_SECRET",
                "vellum_secret_name": value.name,
            }

        if isinstance(value, ExecutionCountReference):
            node_class_display = display_context.global_node_displays[value.node_class]

            return {
                "type": "EXECUTION_COUNTER",
                "node_id": str(node_class_display.node_id),
            }

        if not isinstance(value, BaseDescriptor):
            vellum_value = primitive_to_vellum_value(value)
            return {
                "type": "CONSTANT_VALUE",
                "value": vellum_value.dict(),
            }

        # If it's not any of the references we know about,
        # then try to serialize it as a nested value
        return self.serialize_condition(display_context, value)
