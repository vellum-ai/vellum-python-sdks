from typing import Any, TypeVar

from vellum.client.types.vellum_variable_type import VellumVariableType
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.references import OutputReference, WorkflowInputReference
from vellum.workflows.references.execution_count import ExecutionCountReference
from vellum.workflows.references.node import NodeReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.utils.vellum_variables import primitive_type_to_vellum_variable_type
from vellum.workflows.vellum_client import create_vellum_client
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.vellum import (
    ConstantValuePointer,
    ExecutionCounterData,
    ExecutionCounterPointer,
    InputVariableData,
    InputVariablePointer,
    NodeInputValuePointerRule,
    NodeOutputData,
    NodeOutputPointer,
    WorkspaceSecretData,
    WorkspaceSecretPointer,
)

_T = TypeVar("_T")


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
    value: Any, display_context: WorkflowDisplayContext
) -> NodeInputValuePointerRule:
    if isinstance(value, OutputReference):
        upstream_node, output_display = display_context.global_node_output_displays[value]
        upstream_node_display = display_context.global_node_displays[upstream_node]
        return NodeOutputPointer(
            data=NodeOutputData(node_id=str(upstream_node_display.node_id), output_id=str(output_display.id)),
        )
    if isinstance(value, WorkflowInputReference):
        workflow_input_display = display_context.global_workflow_input_displays[value]
        return InputVariablePointer(data=InputVariableData(input_variable_id=str(workflow_input_display.id)))
    if isinstance(value, VellumSecretReference):
        # TODO: Pass through the name instead of retrieving the ID
        # https://app.shortcut.com/vellum/story/5072
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
