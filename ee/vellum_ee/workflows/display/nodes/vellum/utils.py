import logging
from uuid import UUID
from typing import Any, List, Optional, Type, Union, cast

from vellum.client.types.json_vellum_value import JsonVellumValue
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.references import NodeReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.exceptions import (
    InvalidOutputReferenceError,
    UnsupportedSerializationException,
    UserFacingException,
)
from vellum_ee.workflows.display.utils.expressions import get_child_descriptor, serialize_value
from vellum_ee.workflows.display.utils.vellum import (
    ConstantValuePointer,
    ExecutionCounterData,
    ExecutionCounterPointer,
    InputVariableData,
    InputVariablePointer,
    NodeInputValuePointerRule,
    WorkspaceSecretData,
    WorkspaceSecretPointer,
    create_node_input_value_pointer_rule,
)
from vellum_ee.workflows.display.vellum import NodeInput, NodeInputValuePointer

logger = logging.getLogger(__name__)


def create_node_input(
    node_id: UUID,
    input_name: str,
    value: Any,
    display_context: WorkflowDisplayContext,
    input_id: Union[Optional[UUID], Optional[str]] = None,
    pointer_type: Optional[Type[NodeInputValuePointerRule]] = ConstantValuePointer,
) -> NodeInput:
    input_id = str(input_id) if input_id else str(uuid4_from_hash(f"{node_id}|{input_name}"))
    try:
        rules = create_node_input_value_pointer_rules(value, display_context, node_id, pointer_type=pointer_type)
    except UserFacingException:
        raise
    except Exception as e:
        display_context.add_validation_error(e)
        rules = []
    return NodeInput(
        id=input_id,
        key=input_name,
        value=NodeInputValuePointer(
            rules=rules,
            combinator="OR",
        ),
    )


def _contains_descriptor(value: Any) -> bool:
    """Check if a value contains any BaseDescriptor objects."""
    if isinstance(value, BaseDescriptor):
        return True
    if isinstance(value, dict):
        return any(_contains_descriptor(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_descriptor(item) for item in value)
    return False


def create_node_input_value_pointer_rules(
    value: Any,
    display_context: WorkflowDisplayContext,
    node_id: UUID,
    existing_rules: Optional[List[NodeInputValuePointerRule]] = None,
    pointer_type: Optional[Type[NodeInputValuePointerRule]] = None,
) -> List[NodeInputValuePointerRule]:
    node_input_value_pointer_rules: List[NodeInputValuePointerRule] = existing_rules or []

    if isinstance(value, BaseDescriptor):
        if isinstance(value, NodeReference):
            if value.instance is None:
                raise ValueError(f"Expected NodeReference {value.name} to have an instance")
            value = cast(BaseDescriptor, value.instance)

        if isinstance(value, LazyReference):
            try:
                child_descriptor = get_child_descriptor(value, display_context)
            except InvalidOutputReferenceError as e:
                logger.warning("Failed to parse lazy reference '%s', skipping serialization", value.name)
                display_context.add_validation_error(e)
                return node_input_value_pointer_rules
            return create_node_input_value_pointer_rules(
                child_descriptor, display_context, node_id, existing_rules=[], pointer_type=pointer_type
            )

        if isinstance(value, CoalesceExpression):
            lhs_rules = create_node_input_value_pointer_rules(
                value.lhs, display_context, node_id, existing_rules=[], pointer_type=pointer_type
            )
            node_input_value_pointer_rules.extend(lhs_rules)

            if not isinstance(value.rhs, CoalesceExpression):
                rhs_rules = create_node_input_value_pointer_rules(
                    value.rhs, display_context, node_id, existing_rules=[], pointer_type=pointer_type
                )
                node_input_value_pointer_rules.extend(rhs_rules)
        else:
            try:
                rule = create_node_input_value_pointer_rule(value, display_context)
            except UnsupportedSerializationException:
                return node_input_value_pointer_rules

            node_input_value_pointer_rules.append(rule)
    elif isinstance(value, (dict, list)) and _contains_descriptor(value):
        display_context.add_validation_error(
            UnsupportedSerializationException(
                "The Vellum UI does not support nested references for this Node attribute. "
                "Consider flattening the references."
            )
        )
        serialized = serialize_value(node_id, display_context, value)
        serialized_pointer = ConstantValuePointer(
            data=JsonVellumValue(value=serialized),
        )
        node_input_value_pointer_rules.append(serialized_pointer)
    else:
        constant_pointer = create_pointer(value, pointer_type)
        node_input_value_pointer_rules.append(constant_pointer)

    return node_input_value_pointer_rules


def create_pointer(
    value: Any,
    pointer_type: Optional[Type[NodeInputValuePointerRule]] = None,
) -> NodeInputValuePointerRule:
    if value is None:
        if pointer_type is WorkspaceSecretPointer:
            return WorkspaceSecretPointer(
                type="WORKSPACE_SECRET", data=WorkspaceSecretData(type="STRING", workspace_secret_id=None)
            )

    vellum_variable_value = primitive_to_vellum_value(value)
    if pointer_type is InputVariablePointer:
        return InputVariablePointer(type="INPUT_VARIABLE", data=InputVariableData(input_variable_id=value))
    elif pointer_type is WorkspaceSecretPointer:
        raise UserFacingException(
            "Secret inputs cannot be set to constant values. "
            "Use a VellumSecretReference or EnvironmentVariableReference instead."
        )
    elif pointer_type is ExecutionCounterPointer:
        return ExecutionCounterPointer(type="EXECUTION_COUNTER", data=ExecutionCounterData(node_id=value))
    elif pointer_type is ConstantValuePointer or pointer_type is None:
        return ConstantValuePointer(type="CONSTANT_VALUE", data=vellum_variable_value)
    else:
        raise ValueError(f"Pointer type {pointer_type} not supported")
