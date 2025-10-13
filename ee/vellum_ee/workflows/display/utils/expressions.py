from dataclasses import asdict, is_dataclass
import inspect
from io import StringIO
import sys
from uuid import UUID
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from pydantic import BaseModel

from vellum.client.types.logical_operator import LogicalOperator
from vellum.workflows.constants import undefined
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
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.nodes.utils import get_unadorned_node
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.references.execution_count import ExecutionCountReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.references.state_value import StateValueReference
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.references.workflow_input import WorkflowInputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.types.generics import is_workflow_class
from vellum.workflows.utils.functions import compile_function_definition
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.utils.exceptions import InvalidInputReferenceError, UnsupportedSerializationException
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileLoader

if TYPE_CHECKING:
    from vellum_ee.workflows.display.types import WorkflowDisplayContext


def virtual_open(file_path: str, mode: str = "r"):
    """
    Open a file, checking VirtualFileFinder instances first before falling back to regular open().
    """
    for finder in sys.meta_path:
        if hasattr(finder, "loader") and isinstance(finder.loader, VirtualFileLoader):
            namespace = finder.loader.namespace
            if file_path.startswith(namespace + "/"):
                relative_path = file_path[len(namespace) + 1 :]
                content = finder.loader._get_code(relative_path)
                if content is not None:
                    return StringIO(content)

    return open(file_path, mode)


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


def _serialize_condition(
    executable_id: UUID, display_context: "WorkflowDisplayContext", condition: BaseDescriptor
) -> JsonObject:
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
        lhs = serialize_value(executable_id, display_context, condition._expression)
        return {
            "type": "UNARY_EXPRESSION",
            "lhs": lhs,
            "operator": convert_descriptor_to_operator(condition),
        }
    elif isinstance(condition, (BetweenExpression, NotBetweenExpression)):
        base = serialize_value(executable_id, display_context, condition._value)
        lhs = serialize_value(executable_id, display_context, condition._start)
        rhs = serialize_value(executable_id, display_context, condition._end)

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
        lhs = serialize_value(executable_id, display_context, condition._lhs)
        rhs = serialize_value(executable_id, display_context, condition._rhs)

        return {
            "type": "BINARY_EXPRESSION",
            "lhs": lhs,
            "operator": convert_descriptor_to_operator(condition),
            "rhs": rhs,
        }
    elif isinstance(condition, AccessorExpression):
        return {
            "type": "BINARY_EXPRESSION",
            "lhs": serialize_value(executable_id, display_context, condition._base),
            "operator": "accessField",
            "rhs": serialize_value(executable_id, display_context, condition._field),
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


def serialize_value(executable_id: UUID, display_context: "WorkflowDisplayContext", value: Any) -> Optional[JsonObject]:
    """
    Serialize a value to a JSON object. Returns `None` if the value resolves to `undefined`.
    This is safe because all valid values are a JSON object, including the `None` constant:
    > `{"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}}`

    Args:
        executable_id: node id or workflow id
        display_context: workflow display context
        value: value to serialize

    Returns:
        serialized value
    """
    if value is undefined:
        return None

    if isinstance(value, ConstantValueReference):
        return serialize_value(executable_id, display_context, value._value)

    if isinstance(value, LazyReference):
        child_descriptor = get_child_descriptor(value, display_context)
        return serialize_value(executable_id, display_context, child_descriptor)

    if isinstance(value, WorkflowInputReference):
        if value not in display_context.global_workflow_input_displays:
            workflow_inputs_class = display_context.workflow_display_class.infer_workflow_class().get_inputs_class()
            if value.inputs_class != workflow_inputs_class:
                inputs_class_name = value.inputs_class.__name__
                workflow_class_name = display_context.workflow_display_class.infer_workflow_class().__name__
                raise UnsupportedSerializationException(
                    f"Inputs class '{inputs_class_name}' referenced during serialization of "
                    f"'{workflow_class_name}' without parameterizing this Workflow with this Inputs definition. "
                    f"Update your Workflow definition to "
                    f"'{workflow_class_name}(BaseWorkflow[{inputs_class_name}, BaseState])'."
                )
            else:
                raise InvalidInputReferenceError(
                    message=f"Inputs class '{value.inputs_class.__qualname__}' has no attribute '{value.name}'",
                    inputs_class_name=value.inputs_class.__qualname__,
                    attribute_name=value.name,
                )
        workflow_input_display = display_context.global_workflow_input_displays[value]
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
        output_display = display_context.global_node_output_displays[value]

        upstream_node_class = value.outputs_class.__parent_class__
        if not issubclass(upstream_node_class, BaseNode):
            raise ValueError(f"Output references must be to a node, not {upstream_node_class}")
        unadorned_upstream_node_class = get_unadorned_node(upstream_node_class)
        upstream_node = display_context.global_node_displays[unadorned_upstream_node_class]

        return {
            "type": "NODE_OUTPUT",
            "node_id": str(upstream_node.node_id),
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

    if isinstance(value, TriggerAttributeReference):
        # Generate trigger ID using the same hash formula as in base_workflow_display.py
        trigger_class = value.trigger_class
        trigger_id = uuid4_from_hash(trigger_class.__qualname__)

        return {
            "type": "TRIGGER_ATTRIBUTE",
            "trigger_id": str(trigger_id),
            "attribute_id": str(value.id),
        }

    if isinstance(value, list):
        serialized_items = []
        for item in value:
            serialized_item = serialize_value(executable_id, display_context, item)
            if serialized_item is not None:
                serialized_items.append(serialized_item)

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
        return serialize_value(executable_id, display_context, dict_value)

    if isinstance(value, dict):
        serialized_entries: List[Dict[str, Any]] = []
        for key, val in value.items():
            serialized_val = serialize_value(executable_id, display_context, val)
            if serialized_val is not None:
                serialized_entries.append(
                    {
                        "id": str(uuid4_from_hash(f"{executable_id}|{key}")),
                        "key": serialize_key(key),
                        "value": serialized_val,
                    }
                )

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

    if isinstance(value, BaseModel):
        context = {"executable_id": executable_id, "client": display_context.client}
        dict_value = value.model_dump(context=context)
        return serialize_value(executable_id, display_context, dict_value)

    if callable(value):
        function_definition = compile_function_definition(value)

        name = function_definition.name
        description = function_definition.description or ""

        inputs = getattr(value, "__vellum_inputs__", {})

        if inputs:
            serialized_inputs = {}
            for param_name, input_ref in inputs.items():
                serialized_input = serialize_value(executable_id, display_context, input_ref)
                if serialized_input is not None:
                    serialized_inputs[param_name] = serialized_input

            model_data = function_definition.model_dump()
            model_data["inputs"] = serialized_inputs
            function_definition_data = model_data
        else:
            function_definition_data = function_definition.model_dump()

        source_path = inspect.getsourcefile(value)
        if source_path is not None:
            with virtual_open(source_path) as f:
                source_code = f.read()
        else:
            source_code = f"Source code not available for {value.__name__}"

        return {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": {
                    "type": "CODE_EXECUTION",
                    "name": name,
                    "description": description,
                    "definition": function_definition_data,
                    "src": source_code,
                },
            },
        }

    if not isinstance(value, BaseDescriptor):
        vellum_value = primitive_to_vellum_value(value)
        return {
            "type": "CONSTANT_VALUE",
            "value": vellum_value.dict(),
        }

    # If it's not any of the references we know about,
    # then try to serialize it as a nested value
    return _serialize_condition(executable_id, display_context, value)
