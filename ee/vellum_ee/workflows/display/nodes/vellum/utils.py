from uuid import UUID
from typing import Any, List, Optional, Type, Union, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.expressions.begins_with import BeginsWithExpression
from vellum.workflows.expressions.between import BetweenExpression
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
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
from vellum.workflows.expressions.less_than import LessThanExpression
from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression
from vellum.workflows.expressions.not_between import NotBetweenExpression
from vellum.workflows.expressions.not_in import NotInExpression
from vellum.workflows.nodes.utils import get_wrapped_node, has_wrapped_node
from vellum.workflows.references import NodeReference, OutputReference
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import create_node_input_value_pointer_rule, primitive_to_vellum_value
from vellum_ee.workflows.display.vellum import (
    ConstantValuePointer,
    ExecutionCounterData,
    ExecutionCounterPointer,
    InputVariableData,
    InputVariablePointer,
    NodeInput,
    NodeInputValuePointer,
    NodeInputValuePointerRule,
    WorkspaceSecretData,
    WorkspaceSecretPointer,
)


def create_node_input(
    node_id: UUID,
    input_name: str,
    value: Any,
    display_context: WorkflowDisplayContext,
    input_id: Union[Optional[UUID], Optional[str]],
    pointer_type: Optional[Type[NodeInputValuePointerRule]] = ConstantValuePointer,
) -> NodeInput:
    input_id = str(input_id) if input_id else str(uuid4_from_hash(f"{node_id}|{input_name}"))
    if (
        isinstance(value, OutputReference)
        and value.outputs_class._node_class
        and has_wrapped_node(value.outputs_class._node_class)
    ):
        wrapped_node = get_wrapped_node(value.outputs_class._node_class)
        if wrapped_node._is_wrapped_node:
            value = getattr(wrapped_node.Outputs, value.name)

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
            if not value.instance:
                raise ValueError(f"Expected NodeReference {value.name} to have an instance")
            value = cast(BaseDescriptor, value.instance)

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


def convert_descriptor_to_operator(descriptor: BaseDescriptor) -> str:
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
    else:
        raise ValueError(f"Unsupported descriptor type: {descriptor}")
