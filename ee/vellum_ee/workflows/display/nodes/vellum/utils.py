from uuid import UUID
from typing import Any, List, Optional, Type, Union, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.references import NodeReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.expressions import get_child_descriptor
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


def create_node_input(
    node_id: UUID,
    input_name: str,
    value: Any,
    display_context: WorkflowDisplayContext,
    input_id: Union[Optional[UUID], Optional[str]] = None,
    pointer_type: Optional[Type[NodeInputValuePointerRule]] = ConstantValuePointer,
) -> NodeInput:
    input_id = str(input_id) if input_id else str(uuid4_from_hash(f"{node_id}|{input_name}"))
    rules = create_node_input_value_pointer_rules(value, display_context, pointer_type=pointer_type)
    return NodeInput(
        id=input_id,
        key=input_name,
        value=NodeInputValuePointer(
            rules=rules,
            combinator="OR",
        ),
    )


def create_node_input_value_pointer_rules(
    value: Any,
    display_context: WorkflowDisplayContext,
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
            child_descriptor = get_child_descriptor(value, display_context)
            return create_node_input_value_pointer_rules(
                child_descriptor, display_context, [], pointer_type=pointer_type
            )

        if isinstance(value, CoalesceExpression):
            # Recursively handle the left-hand side
            lhs_rules = create_node_input_value_pointer_rules(value.lhs, display_context, [], pointer_type=pointer_type)
            node_input_value_pointer_rules.extend(lhs_rules)

            # Handle the right-hand side
            if not isinstance(value.rhs, CoalesceExpression):
                rhs_rules = create_node_input_value_pointer_rules(
                    value.rhs, display_context, [], pointer_type=pointer_type
                )
                node_input_value_pointer_rules.extend(rhs_rules)
        else:
            # Non-CoalesceExpression case
            node_input_value_pointer_rules.append(create_node_input_value_pointer_rule(value, display_context))
    else:
        pointer = create_pointer(value, pointer_type)
        node_input_value_pointer_rules.append(pointer)

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
        return WorkspaceSecretPointer(
            type="WORKSPACE_SECRET", data=WorkspaceSecretData(type="STRING", workspace_secret_id=value)
        )
    elif pointer_type is ExecutionCounterPointer:
        return ExecutionCounterPointer(type="EXECUTION_COUNTER", data=ExecutionCounterData(node_id=value))
    elif pointer_type is ConstantValuePointer or pointer_type is None:
        return ConstantValuePointer(type="CONSTANT_VALUE", data=vellum_variable_value)
    else:
        raise ValueError(f"Pointer type {pointer_type} not supported")
