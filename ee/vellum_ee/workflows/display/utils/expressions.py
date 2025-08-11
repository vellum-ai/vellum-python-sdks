from dataclasses import asdict, is_dataclass
from typing import TYPE_CHECKING, Any, Dict, List, cast

from pydantic import BaseModel

from vellum.client.types.logical_operator import LogicalOperator
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.expressions.accessor import AccessorExpression
from vellum.workflows.expressions.add import AddExpression
from vellum.workflows.expressions.and_ import AndExpression
from vellum.workflows.expressions.begins_with import BeginsWithExpression
from vellum.workflows.expressions.between import BetweenExpression
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.expressions.concat import ConcatExpression
from vellum.workflows.expressions.contains import ContainsExpression
from vellum.workflows.expressions.does_not_begin_with import DoesNotBeginWithExpression
from vellum.workflows.expressions.does_not_contain import DoesNotContainExpression
from vellum.workflows.expressions.does_not_end_with import DoesNotEndWithExpression
from vellum.workflows.expressions.does_not_equal import DoesNotEqualExpression
from vellum.workflows.expressions.ends_with import EndsWithExpression
from vellum.workflows.expressions.equals import EqualsExpression
from vellum.workflows.expressions.greater_than import GreaterThanExpression
from vellum.workflows.expressions.greater_than_or_equal_to import GreaterThanOrEqualToExpression
from vellum.workflows.expressions.in_ import InExpression
from vellum.workflows.expressions.is_nil import IsNilExpression
from vellum.workflows.expressions.is_not_nil import IsNotNilExpression
from vellum.workflows.expressions.is_not_null import IsNotNullExpression
from vellum.workflows.expressions.is_not_undefined import IsNotUndefinedExpression
from vellum.workflows.expressions.is_null import IsNullExpression
from vellum.workflows.expressions.is_undefined import IsUndefinedExpression
from vellum.workflows.expressions.length import LengthExpression
from vellum.workflows.expressions.less_than import LessThanExpression
from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression
from vellum.workflows.expressions.minus import MinusExpression
from vellum.workflows.expressions.not_between import NotBetweenExpression
from vellum.workflows.expressions.not_in import NotInExpression
from vellum.workflows.expressions.or_ import OrExpression
from vellum.workflows.expressions.parse_json import ParseJsonExpression
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.references.execution_count import ExecutionCountReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.references.state_value import StateValueReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.references.workflow_input import WorkflowInputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.types.definition import DeploymentDefinition
from vellum.workflows.types.generics import is_workflow_class
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.utils.exceptions import UnsupportedSerializationException

if TYPE_CHECKING:
    from vellum_ee.workflows.display.types import WorkflowDisplayContext


def convert_descriptor_to_operator(descriptor: BaseDescriptor) -> LogicalOperator:
    if isinstance(descriptor, EqualsExpression):
        return "="
    elif isinstance(descriptor, DoesNotEqualExpression):
        return "!="
    elif isinstance(descriptor, LessThanExpression):
        return "<"
    elif isinstance(descriptor, GreaterThanExpression):
        return ">"
    elif isinstance(descriptor, LessThanOrEqualToExpression):
        return "<="
    elif isinstance(descriptor, GreaterThanOrEqualToExpression):
        return ">="
    elif isinstance(descriptor, ContainsExpression):
        return "contains"
    elif isinstance(descriptor, BeginsWithExpression):
        return "beginsWith"
    elif isinstance(descriptor, EndsWithExpression):
        return "endsWith"
    elif isinstance(descriptor, DoesNotContainExpression):
        return "doesNotContain"
    elif isinstance(descriptor, DoesNotBeginWithExpression):
        return "doesNotBeginWith"
    elif isinstance(descriptor, DoesNotEndWithExpression):
        return "doesNotEndWith"
    elif isinstance(descriptor, (IsNullExpression, IsNilExpression, IsUndefinedExpression)):
        return "null"
    elif isinstance(descriptor, (IsNotNullExpression, IsNotNilExpression, IsNotUndefinedExpression)):
        return "notNull"
    elif isinstance(descriptor, InExpression):
        return "in"
    elif isinstance(descriptor, NotInExpression):
        return "notIn"
    elif isinstance(descriptor, BetweenExpression):
        return "between"
    elif isinstance(descriptor, NotBetweenExpression):
        return "notBetween"
    elif isinstance(descriptor, AndExpression):
        return "and"
    elif isinstance(descriptor, OrExpression):
        return "or"
    elif isinstance(descriptor, CoalesceExpression):
        return "coalesce"
    elif isinstance(descriptor, ParseJsonExpression):
        return "parseJson"
    elif isinstance(descriptor, LengthExpression):
        return "length"
    elif isinstance(descriptor, AddExpression):
        return "+"
    elif isinstance(descriptor, MinusExpression):
        return "-"
    elif isinstance(descriptor, ConcatExpression):
        return "concat"
    else:
        raise ValueError(f"Unsupported descriptor type: {descriptor}")


def get_child_descriptor(value: LazyReference, display_context: "WorkflowDisplayContext") -> BaseDescriptor:
    if isinstance(value._get, str):
        reference_parts = value._get.split(".")
        if len(reference_parts) < 3:
            raise Exception(f"Failed to parse lazy reference: {value._get}. Only Node Output references are supported.")

        output_name = reference_parts[-1]
        nested_class_name = reference_parts[-2]
        if nested_class_name != "Outputs":
            raise Exception(
                f"Failed to parse lazy reference: {value._get}. Outputs are the only node reference supported."
            )

        node_class_name = ".".join(reference_parts[:-2])
        for node in display_context.global_node_displays.keys():
            if node.__name__ == node_class_name:
                return getattr(node.Outputs, output_name)

        raise Exception(f"Failed to parse lazy reference: {value._get}")

    return value._get()


def _serialize_condition(display_context: "WorkflowDisplayContext", condition: BaseDescriptor) -> JsonObject:
    if isinstance(
        condition,
        (
            IsNullExpression,
            IsNotNullExpression,
            IsNilExpression,
            IsNotNilExpression,
            IsUndefinedExpression,
            IsNotUndefinedExpression,
            LengthExpression,
            ParseJsonExpression,
        ),
    ):
        lhs = serialize_value(display_context, condition._expression)
        return {
            "type": "UNARY_EXPRESSION",
            "lhs": lhs,
            "operator": convert_descriptor_to_operator(condition),
        }
    elif isinstance(condition, (BetweenExpression, NotBetweenExpression)):
        base = serialize_value(display_context, condition._value)
        lhs = serialize_value(display_context, condition._start)
        rhs = serialize_value(display_context, condition._end)

        return {
            "type": "TERNARY_EXPRESSION",
            "base": base,
            "operator": convert_descriptor_to_operator(condition),
            "lhs": lhs,
            "rhs": rhs,
        }
    elif isinstance(
        condition,
        (
            AddExpression,
            AndExpression,
            BeginsWithExpression,
            CoalesceExpression,
            ConcatExpression,
            ContainsExpression,
            DoesNotBeginWithExpression,
            DoesNotContainExpression,
            DoesNotEndWithExpression,
            DoesNotEqualExpression,
            EndsWithExpression,
            EqualsExpression,
            GreaterThanExpression,
            GreaterThanOrEqualToExpression,
            InExpression,
            LessThanExpression,
            LessThanOrEqualToExpression,
            MinusExpression,
            NotInExpression,
            OrExpression,
        ),
    ):
        lhs = serialize_value(display_context, condition._lhs)
        rhs = serialize_value(display_context, condition._rhs)

        return {
            "type": "BINARY_EXPRESSION",
            "lhs": lhs,
            "operator": convert_descriptor_to_operator(condition),
            "rhs": rhs,
        }
    elif isinstance(condition, AccessorExpression):
        return {
            "type": "BINARY_EXPRESSION",
            "lhs": serialize_value(display_context, condition._base),
            "operator": "accessField",
            "rhs": serialize_value(display_context, condition._field),
        }

    raise UnsupportedSerializationException(f"Unsupported condition type: {condition.__class__.__name__}")


def serialize_key(key: Any) -> str:
    """Serialize dictionary keys to strings, handling function objects properly."""
    if callable(key):
        return key.__name__
    elif isinstance(key, str):
        return key
    else:
        return str(key)


def serialize_value(display_context: "WorkflowDisplayContext", value: Any) -> JsonObject:
    if isinstance(value, ConstantValueReference):
        return serialize_value(display_context, value._value)

    if isinstance(value, LazyReference):
        child_descriptor = get_child_descriptor(value, display_context)
        return serialize_value(display_context, child_descriptor)

    if isinstance(value, WorkflowInputReference):
        try:
            workflow_input_display = display_context.global_workflow_input_displays[value]
        except KeyError:
            inputs_class_name = value.inputs_class.__name__
            workflow_class_name = display_context.workflow_display_class.infer_workflow_class().__name__
            raise UnsupportedSerializationException(
                f"Inputs class '{inputs_class_name}' referenced during serialization of '{workflow_class_name}' "
                f"without parameterizing this Workflow with this Inputs definition. Update your Workflow "
                f"definition to '{workflow_class_name}(BaseWorkflow[{inputs_class_name}, BaseState])'."
            )
        return {
            "type": "WORKFLOW_INPUT",
            "input_variable_id": str(workflow_input_display.id),
        }

    if isinstance(value, StateValueReference):
        state_value_display = display_context.global_state_value_displays[value]
        return {
            "type": "WORKFLOW_STATE",
            "state_variable_id": str(state_value_display.id),
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

    if isinstance(value, EnvironmentVariableReference):
        if value.serialize_as_constant:
            return {
                "type": "CONSTANT_VALUE",
                "value": {
                    "type": "STRING",
                    "value": value.name,
                },
            }
        else:
            return {
                "type": "ENVIRONMENT_VARIABLE",
                "environment_variable": value.name,
            }

    if isinstance(value, ExecutionCountReference):
        node_class_display = display_context.global_node_displays[value.node_class]

        return {
            "type": "EXECUTION_COUNTER",
            "node_id": str(node_class_display.node_id),
        }

    if isinstance(value, list):
        serialized_items = [serialize_value(display_context, item) for item in value]
        if all(isinstance(item, dict) and item["type"] == "CONSTANT_VALUE" for item in serialized_items):
            constant_values = []
            for item in serialized_items:
                item_dict = cast(Dict[str, Any], item)
                value_inner = item_dict["value"]

                if value_inner["type"] == "JSON" and "items" in value_inner:
                    # Nested JSON list
                    constant_values.append(value_inner["items"])
                else:
                    constant_values.append(value_inner["value"])

            return {
                "type": "CONSTANT_VALUE",
                "value": {
                    "type": "JSON",
                    "value": constant_values,
                },
            }
        else:
            return {
                "type": "ARRAY_REFERENCE",
                "items": cast(JsonArray, serialized_items),  # list[JsonObject] -> JsonArray
            }

    if is_dataclass(value) and not isinstance(value, type):
        dict_value = asdict(value)
        return serialize_value(display_context, dict_value)

    if isinstance(value, dict):
        serialized_entries: List[Dict[str, Any]] = [
            {
                "id": str(uuid4_from_hash(f"{key}|{val}")),
                "key": serialize_key(key),
                "value": serialize_value(display_context, val),
            }
            for key, val in value.items()
        ]

        # Check if all entries have constant values
        if all(entry["value"]["type"] == "CONSTANT_VALUE" for entry in serialized_entries):
            constant_entries = {}
            for entry in serialized_entries:
                entry_value = entry["value"]["value"]
                constant_entries[entry["key"]] = entry_value["value"]

            return {
                "type": "CONSTANT_VALUE",
                "value": {
                    "type": "JSON",
                    "value": constant_entries,
                },
            }
        else:
            return {"type": "DICTIONARY_REFERENCE", "entries": cast(JsonArray, serialized_entries)}

    if is_workflow_class(value):
        from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

        # Pass the parent display context so the subworkflow can resolve parent workflow inputs
        workflow_display = get_workflow_display(
            workflow_class=value,
            parent_display_context=display_context,
        )
        serialized_value: dict = workflow_display.serialize()
        name = serialized_value["workflow_raw_data"]["definition"]["name"]
        description = value.__doc__ or ""
        return {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": {
                    "type": "INLINE_WORKFLOW",
                    "name": name,
                    "description": description,
                    "exec_config": serialized_value,
                },
            },
        }

    if isinstance(value, DeploymentDefinition):
        workflow_deployment_release = display_context.client.workflow_deployments.retrieve_workflow_deployment_release(
            value.deployment, value.release_tag
        )
        name = workflow_deployment_release.deployment.name or value.deployment
        description = workflow_deployment_release.description or f"Workflow Deployment for {name}"

        return {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": {
                    "type": "WORKFLOW_DEPLOYMENT",
                    "name": name,
                    "description": description,
                    "deployment": value.deployment,
                    "release_tag": value.release_tag,
                },
            },
        }

    if isinstance(value, BaseModel):
        dict_value = value.model_dump()
        return serialize_value(display_context, dict_value)

    if not isinstance(value, BaseDescriptor):
        vellum_value = primitive_to_vellum_value(value)
        return {
            "type": "CONSTANT_VALUE",
            "value": vellum_value.dict(),
        }

    # If it's not any of the references we know about,
    # then try to serialize it as a nested value
    return _serialize_condition(display_context, value)
