from uuid import UUID
from typing import Any, List, Literal, Optional, Tuple, Type, Union, cast

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.references import NodeReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.expressions import get_child_descriptor
from vellum_ee.workflows.display.utils.vellum import NodeInputValuePointerRule, create_node_input_value_pointer_rule


class NodeInputValuePointer(UniversalBaseModel):
    rules: List[NodeInputValuePointerRule]
    combinator: Literal["OR"] = "OR"


class NodeInput(UniversalBaseModel):
    id: str
    key: str
    value: NodeInputValuePointer


def create_node_input(
    node_id: UUID,
    input_name: str,
    value: Any,
    display_context: WorkflowDisplayContext,
    input_id: Union[Optional[UUID], Optional[str]] = None,
    expected_types: Optional[Tuple[Type, ...]] = None,
) -> NodeInput:
    input_id = str(input_id) if input_id else str(uuid4_from_hash(f"{node_id}|{input_name}"))
    rules = create_node_input_value_pointer_rules(value, display_context, expected_types=expected_types)
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
    expected_types: Optional[Tuple[Type, ...]] = None,
) -> List[NodeInputValuePointerRule]:
    node_input_value_pointer_rules: List[NodeInputValuePointerRule] = existing_rules or []

    if isinstance(value, NodeReference):
        if value.instance is None:
            raise ValueError(f"Expected NodeReference {value.name} to have an instance")
        value = cast(BaseDescriptor, value.instance)

    if isinstance(value, LazyReference):
        child_descriptor = get_child_descriptor(value, display_context)
        return create_node_input_value_pointer_rules(child_descriptor, display_context, expected_types=expected_types)

    if isinstance(value, CoalesceExpression):
        # Recursively handle the left-hand side
        lhs_rules = create_node_input_value_pointer_rules(value.lhs, display_context, expected_types=expected_types)
        node_input_value_pointer_rules.extend(lhs_rules)

        # Handle the right-hand side
        if not isinstance(value.rhs, CoalesceExpression):
            rhs_rules = create_node_input_value_pointer_rules(
                value.rhs, display_context, [], expected_types=expected_types
            )
            node_input_value_pointer_rules.extend(rhs_rules)
    else:
        # Non-CoalesceExpression case
        node_input_value_pointer_rules.append(
            create_node_input_value_pointer_rule(value, display_context, expected_types=expected_types)
        )

    return node_input_value_pointer_rules
