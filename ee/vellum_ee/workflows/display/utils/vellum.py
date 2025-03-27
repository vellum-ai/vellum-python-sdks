from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.array_vellum_value import ArrayVellumValue
from vellum.client.types.logical_operator import LogicalOperator
from vellum.client.types.vellum_value import VellumValue
from vellum.client.types.vellum_variable_type import VellumVariableType
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.expressions.and_ import AndExpression
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
from vellum.workflows.expressions.or_ import OrExpression
from vellum.workflows.expressions.parse_json import ParseJsonExpression
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.references import OutputReference, WorkflowInputReference
from vellum.workflows.references.execution_count import ExecutionCountReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.node import NodeReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.utils.vellum_variables import primitive_type_to_vellum_variable_type
from vellum.workflows.vellum_client import create_vellum_client
from vellum_ee.workflows.display.utils.expressions import get_child_descriptor

if TYPE_CHECKING:
    from vellum_ee.workflows.display.types import WorkflowDisplayContext


class ConstantValuePointer(UniversalBaseModel):
    type: Literal["CONSTANT_VALUE"] = "CONSTANT_VALUE"
    data: VellumValue


ArrayVellumValue.model_rebuild()


class NodeOutputData(UniversalBaseModel):
    node_id: str
    output_id: str


class NodeOutputPointer(UniversalBaseModel):
    type: Literal["NODE_OUTPUT"] = "NODE_OUTPUT"
    data: NodeOutputData


class InputVariableData(UniversalBaseModel):
    input_variable_id: str


class InputVariablePointer(UniversalBaseModel):
    type: Literal["INPUT_VARIABLE"] = "INPUT_VARIABLE"
    data: InputVariableData


class WorkspaceSecretData(UniversalBaseModel):
    type: VellumVariableType
    workspace_secret_id: Optional[str] = None


class WorkspaceSecretPointer(UniversalBaseModel):
    type: Literal["WORKSPACE_SECRET"] = "WORKSPACE_SECRET"
    data: WorkspaceSecretData


class ExecutionCounterData(UniversalBaseModel):
    node_id: str


class ExecutionCounterPointer(UniversalBaseModel):
    type: Literal["EXECUTION_COUNTER"] = "EXECUTION_COUNTER"
    data: ExecutionCounterData


NodeInputValuePointerRule = Union[
    NodeOutputPointer,
    InputVariablePointer,
    ConstantValuePointer,
    WorkspaceSecretPointer,
    ExecutionCounterPointer,
]


def infer_vellum_variable_type(value: Any) -> VellumVariableType:
    inferred_type: VellumVariableType

    if isinstance(value, BaseDescriptor):
        descriptor: BaseDescriptor = value
        if isinstance(descriptor, NodeReference):
            if not isinstance(descriptor.instance, BaseDescriptor):
                raise ValueError(
                    f"Expected NodeReference {descriptor.name} to have an instance pointing to a descriptor"
                )
            descriptor = descriptor.instance

        inferred_type = primitive_type_to_vellum_variable_type(descriptor)
    else:
        vellum_variable_value = primitive_to_vellum_value(value)
        inferred_type = vellum_variable_value.type

    return inferred_type


def create_node_input_value_pointer_rule(
    value: Any, display_context: "WorkflowDisplayContext"
) -> NodeInputValuePointerRule:
    if isinstance(value, OutputReference):
        if value not in display_context.global_node_output_displays:
            if issubclass(value.outputs_class, BaseNode.Outputs):
                raise ValueError(f"Reference to node '{value.outputs_class._node_class.__name__}' not found in graph.")

            raise ValueError(f"Reference to outputs '{value.outputs_class.__qualname__}' is invalid.")

        upstream_node, output_display = display_context.global_node_output_displays[value]
        upstream_node_display = display_context.global_node_displays[upstream_node]
        return NodeOutputPointer(
            data=NodeOutputData(node_id=str(upstream_node_display.node_id), output_id=str(output_display.id)),
        )
    if isinstance(value, LazyReference):
        child_descriptor = get_child_descriptor(value, display_context)
        return create_node_input_value_pointer_rule(child_descriptor, display_context)
    if isinstance(value, WorkflowInputReference):
        workflow_input_display = display_context.global_workflow_input_displays[value]
        return InputVariablePointer(data=InputVariableData(input_variable_id=str(workflow_input_display.id)))
    if isinstance(value, VellumSecretReference):
        vellum_client = create_vellum_client()
        workspace_secret = vellum_client.workspace_secrets.retrieve(
            id=value.name,
        )
        return WorkspaceSecretPointer(
            data=WorkspaceSecretData(
                type="STRING",
                workspace_secret_id=str(workspace_secret.id),
            ),
        )
    if isinstance(value, ExecutionCountReference):
        node_class_display = display_context.node_displays[value.node_class]
        return ExecutionCounterPointer(
            data=ExecutionCounterData(node_id=str(node_class_display.node_id)),
        )

    if not isinstance(value, BaseDescriptor):
        vellum_value = primitive_to_vellum_value(value)
        return ConstantValuePointer(type="CONSTANT_VALUE", data=vellum_value)

    raise ValueError(f"Unsupported descriptor type: {value.__class__.__name__}")


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
    else:
        raise ValueError(f"Unsupported descriptor type: {descriptor}")
