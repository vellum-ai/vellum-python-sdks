from uuid import UUID
from typing import Any, Generic, List, Optional, TypeVar

from vellum.client import Vellum as VellumClient
from vellum.utils.uuid import is_valid_uuid
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.expressions import serialize_value
from vellum_ee.workflows.display.vellum import NodeInput

_SubworkflowDeploymentNodeType = TypeVar("_SubworkflowDeploymentNodeType", bound=SubworkflowDeploymentNode)


class BaseSubworkflowDeploymentNodeDisplay(
    BaseNodeDisplay[_SubworkflowDeploymentNodeType], Generic[_SubworkflowDeploymentNodeType]
):
    __serializable_inputs__ = {SubworkflowDeploymentNode.subworkflow_inputs}

    _deployment_id: Optional[str] = None
    _release_tag: Optional[str] = None

    def build(self, client: VellumClient) -> None:
        node = self._node
        deployment_descriptor_id = str(raise_if_descriptor(node.deployment))
        self._release_tag = raise_if_descriptor(node.release_tag)

        deployment_release = client.workflow_deployments.retrieve_workflow_deployment_release(
            id=deployment_descriptor_id,
            release_id_or_release_tag=self._release_tag,
        )
        self._deployment_id = str(deployment_release.deployment.id)
        output_variables_by_key = {var.key: var for var in deployment_release.workflow_version.output_variables}

        for output in node.Outputs:
            original_output_display = self.output_display.get(output)
            if original_output_display and not original_output_display._is_implicit:
                continue

            output_variable = output_variables_by_key.get(output.name)
            if not output_variable or not is_valid_uuid(output_variable.id):
                continue

            output_id = UUID(output_variable.id)
            self.output_display[output] = NodeOutputDisplay(
                id=output_id,
                name=output.name,
            )
            self._node.__output_ids__[output.name] = output_id

    def _create_subworkflow_input(
        self,
        node_id: UUID,
        input_name: str,
        value: Any,
        display_context: WorkflowDisplayContext,
    ) -> NodeInput:
        input_id = self.node_input_ids_by_name.get(
            f"{SubworkflowDeploymentNode.subworkflow_inputs.name}.{input_name}"
        ) or self.node_input_ids_by_name.get(input_name)

        return create_node_input(
            node_id=node_id,
            input_name=input_name,
            value=value,
            display_context=display_context,
            input_id=input_id,
        )

    def _serialize_subworkflow_inputs_attribute(
        self,
        node_id: UUID,
        display_context: WorkflowDisplayContext,
    ) -> JsonObject:
        """Serialize subworkflow_inputs as an attribute using DICTIONARY_REFERENCE pattern."""
        node = self._node
        subworkflow_inputs = raise_if_descriptor(node.subworkflow_inputs)

        if isinstance(subworkflow_inputs, BaseInputs):
            inputs_dict = {input_descriptor.name: input_value for input_descriptor, input_value in subworkflow_inputs}
        else:
            inputs_dict = dict(subworkflow_inputs)

        attr_id = self.attribute_ids_by_name.get(SubworkflowDeploymentNode.subworkflow_inputs.name) or uuid4_from_hash(
            f"{node_id}|{SubworkflowDeploymentNode.subworkflow_inputs.name}"
        )

        return {
            "id": str(attr_id),
            "name": SubworkflowDeploymentNode.subworkflow_inputs.name,
            "value": serialize_value(node_id, display_context, inputs_dict),
        }

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **_kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        subworkflow_inputs = raise_if_descriptor(node.subworkflow_inputs)

        if isinstance(subworkflow_inputs, BaseInputs):
            input_items = [(input_descriptor.name, input_value) for input_descriptor, input_value in subworkflow_inputs]
        else:
            input_items = list(subworkflow_inputs.items())

        node_inputs: List[NodeInput] = [
            self._create_subworkflow_input(
                node_id=node_id,
                input_name=variable_name,
                value=variable_value,
                display_context=display_context,
            )
            for variable_name, variable_value in input_items
        ]

        attributes: JsonArray = [self._serialize_subworkflow_inputs_attribute(node_id, display_context)]

        return {
            "id": str(node_id),
            "type": "SUBWORKFLOW",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "error_output_id": str(error_output_id) if error_output_id else None,
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "variant": "DEPLOYMENT",
                "workflow_deployment_id": self._deployment_id,
                "release_tag": self._release_tag,
            },
            "attributes": attributes,
            **self.serialize_generic_fields(display_context),
        }
