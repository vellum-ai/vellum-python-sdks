from uuid import UUID
from typing import Generic, Optional, TypeVar

from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.types.core import JsonObject
from vellum.workflows.vellum_client import create_vellum_client
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_SubworkflowDeploymentNodeType = TypeVar("_SubworkflowDeploymentNodeType", bound=SubworkflowDeploymentNode)


class BaseSubworkflowDeploymentNodeDisplay(
    BaseNodeVellumDisplay[_SubworkflowDeploymentNodeType], Generic[_SubworkflowDeploymentNodeType]
):

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        subworkflow_inputs = raise_if_descriptor(node.subworkflow_inputs)
        node_inputs = [
            create_node_input(
                node_id=node_id,
                input_name=variable_name,
                value=variable_value,
                display_context=display_context,
                input_id=self.node_input_ids_by_name.get(variable_name),
            )
            for variable_name, variable_value in subworkflow_inputs.items()
        ]

        # TODO: Pass through the name instead of retrieving the ID
        # https://app.shortcut.com/vellum/story/4702
        vellum_client = create_vellum_client()
        deployment = vellum_client.workflow_deployments.retrieve(
            id=str(raise_if_descriptor(node.deployment)),
        )

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
                "workflow_deployment_id": str(deployment.id),
                "release_tag": raise_if_descriptor(node.release_tag),
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
        }
