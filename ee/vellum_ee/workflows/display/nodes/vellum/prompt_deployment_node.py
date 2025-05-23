from uuid import UUID
from typing import Generic, Optional, TypeVar

from vellum.workflows.nodes.displayable.prompt_deployment_node import PromptDeploymentNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_PromptDeploymentNodeType = TypeVar("_PromptDeploymentNodeType", bound=PromptDeploymentNode)


class BasePromptDeploymentNodeDisplay(BaseNodeDisplay[_PromptDeploymentNodeType], Generic[_PromptDeploymentNodeType]):
    __serializable_inputs__ = {PromptDeploymentNode.prompt_inputs}

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        prompt_inputs = raise_if_descriptor(node.prompt_inputs)
        node_inputs = (
            [
                create_node_input(
                    node_id=node_id,
                    input_name=variable_name,
                    value=variable_value,
                    display_context=display_context,
                    input_id=self.node_input_ids_by_name.get(
                        f"{PromptDeploymentNode.prompt_inputs.name}.{variable_name}"
                    )
                    or self.node_input_ids_by_name.get(variable_name),
                )
                for variable_name, variable_value in prompt_inputs.items()
            ]
            if prompt_inputs
            else []
        )

        output_display = self.output_display[node.Outputs.text]
        array_display = self.output_display[node.Outputs.results]
        json_display = self.output_display[node.Outputs.json]

        deployment = display_context.client.deployments.retrieve(
            id=str(raise_if_descriptor(node.deployment)),
        )
        ml_model_fallbacks = raise_if_descriptor(node.ml_model_fallbacks)

        return {
            "id": str(node_id),
            "type": "PROMPT",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "output_id": str(output_display.id),
                "error_output_id": str(error_output_id) if error_output_id else None,
                "array_output_id": str(array_display.id),
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "variant": "DEPLOYMENT",
                "prompt_deployment_id": str(deployment.id),
                "release_tag": raise_if_descriptor(node.release_tag),
                "ml_model_fallbacks": list(ml_model_fallbacks) if ml_model_fallbacks else None,
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
            "ports": self.serialize_ports(display_context),
            "outputs": [
                {"id": str(json_display.id), "name": "json", "type": "JSON", "value": None},
                {"id": str(output_display.id), "name": "text", "type": "STRING", "value": None},
                {"id": str(array_display.id), "name": "results", "type": "ARRAY", "value": None},
            ],
        }
