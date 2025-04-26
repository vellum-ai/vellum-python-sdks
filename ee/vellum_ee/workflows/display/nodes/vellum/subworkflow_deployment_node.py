from uuid import UUID
from typing import Generic, Optional, TypeVar

from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_SubworkflowDeploymentNodeType = TypeVar("_SubworkflowDeploymentNodeType", bound=SubworkflowDeploymentNode)


class BaseSubworkflowDeploymentNodeDisplay(
    BaseNodeDisplay[_SubworkflowDeploymentNodeType], Generic[_SubworkflowDeploymentNodeType]
):
    __serializable_inputs__ = {SubworkflowDeploymentNode.subworkflow_inputs}

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
                input_id=self.node_input_ids_by_name.get(
                    f"{SubworkflowDeploymentNode.subworkflow_inputs.name}.{variable_name}"
                )
                or self.node_input_ids_by_name.get(variable_name),
            )
            for variable_name, variable_value in subworkflow_inputs.items()
        ]

        deployment = display_context.client.workflow_deployments.retrieve(
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
            "ports": self.serialize_ports(display_context),
        }
