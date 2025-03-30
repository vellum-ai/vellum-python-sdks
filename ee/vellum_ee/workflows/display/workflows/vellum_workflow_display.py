import logging
from uuid import UUID
from typing import Optional, cast

from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.nodes.utils import get_unadorned_node, get_unadorned_port
from vellum.workflows.references import WorkflowInputReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type
from vellum_ee.workflows.display.vellum import WorkflowInputsVellumDisplay, WorkflowInputsVellumDisplayOverrides
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay

logger = logging.getLogger(__name__)


class VellumWorkflowDisplay(
    BaseWorkflowDisplay[
        WorkflowType,
        WorkflowInputsVellumDisplay,
        WorkflowInputsVellumDisplayOverrides,
    ]
):
    node_display_base_class = BaseNodeDisplay

    def serialize(self) -> JsonObject:
        input_variables: JsonArray = []
        for workflow_input, workflow_input_display in self.display_context.workflow_input_displays.items():
            default = primitive_to_vellum_value(workflow_input.instance) if workflow_input.instance else None
            required = (
                workflow_input_display.required
                if workflow_input_display.required is not None
                else type(None) not in workflow_input.types
            )

            input_variables.append(
                {
                    "id": str(workflow_input_display.id),
                    "key": workflow_input_display.name or workflow_input.name,
                    "type": infer_vellum_variable_type(workflow_input),
                    "default": default.dict() if default else None,
                    "required": required,
                    "extensions": {"color": workflow_input_display.color},
                }
            )

        state_variables: JsonArray = []
        for state_value_reference, state_value_display in self.display_context.state_value_displays.items():
            default = (
                primitive_to_vellum_value(state_value_reference.instance) if state_value_reference.instance else None
            )
            state_variables.append(
                {
                    "id": str(state_value_display.id),
                    "key": state_value_display.name or state_value_reference.name,
                    "type": infer_vellum_variable_type(state_value_reference),
                    "default": default.dict() if default else None,
                    "required": state_value_reference.instance is None,
                    "extensions": {"color": state_value_display.color},
                }
            )

        nodes: JsonArray = []
        edges: JsonArray = []

        # Add a single synthetic node for the workflow entrypoint
        entrypoint_node_id = self.display_context.workflow_display.entrypoint_node_id
        entrypoint_node_source_handle_id = self.display_context.workflow_display.entrypoint_node_source_handle_id
        nodes.append(
            {
                "id": str(entrypoint_node_id),
                "type": "ENTRYPOINT",
                "inputs": [],
                "data": {
                    "label": "Entrypoint Node",
                    "source_handle_id": str(entrypoint_node_source_handle_id),
                },
                "display_data": self.display_context.workflow_display.entrypoint_node_display.dict(),
                "base": None,
                "definition": None,
            },
        )

        # Add all the nodes in the workflow
        for node in self._workflow.get_nodes():
            node_display = self.display_context.node_displays[node]

            try:
                serialized_node = node_display.serialize(self.display_context)
            except NotImplementedError as e:
                self.add_error(e)
                continue

            nodes.append(serialized_node)

        # Add all unused nodes in the workflow
        for node in self._workflow.get_unused_nodes():
            node_display = self.display_context.node_displays[node]

            try:
                serialized_node = node_display.serialize(self.display_context)
            except NotImplementedError as e:
                self.add_error(e)
                continue

            nodes.append(serialized_node)

        synthetic_output_edges: JsonArray = []
        output_variables: JsonArray = []
        final_output_nodes = [
            node for node in self.display_context.node_displays.keys() if issubclass(node, FinalOutputNode)
        ]
        final_output_node_outputs = {node.Outputs.value for node in final_output_nodes}
        unreferenced_final_output_node_outputs = final_output_node_outputs.copy()
        final_output_node_base: JsonObject = {
            "name": FinalOutputNode.__name__,
            "module": cast(JsonArray, FinalOutputNode.__module__.split(".")),
        }

        # Add a synthetic Terminal Node and track the Workflow's output variables for each Workflow output
        for workflow_output, workflow_output_display in self.display_context.workflow_output_displays.items():
            final_output_node_id = uuid4_from_hash(f"{self.workflow_id}|node_id|{workflow_output.name}")
            inferred_type = infer_vellum_variable_type(workflow_output)

            # Remove the terminal node output from the unreferenced set
            unreferenced_final_output_node_outputs.discard(cast(OutputReference, workflow_output.instance))

            if workflow_output.instance not in final_output_node_outputs:
                # Create a synthetic terminal node only if there is no terminal node for this output
                try:
                    node_input = create_node_input(
                        final_output_node_id,
                        "node_input",
                        # This is currently the wrapper node's output, but we want the wrapped node
                        workflow_output.instance,
                        self.display_context,
                    )
                except ValueError as e:
                    raise ValueError(f"Failed to serialize output '{workflow_output.name}': {str(e)}") from e

                source_node_display: Optional[BaseNodeDisplay]
                first_rule = node_input.value.rules[0]
                if first_rule.type == "NODE_OUTPUT":
                    source_node_id = UUID(first_rule.data.node_id)
                    try:
                        source_node_display = [
                            node_display
                            for node_display in self.display_context.node_displays.values()
                            if node_display.node_id == source_node_id
                        ][0]
                    except IndexError:
                        source_node_display = None

                synthetic_target_handle_id = str(
                    uuid4_from_hash(f"{self.workflow_id}|target_handle_id|{workflow_output_display.name}")
                )
                synthetic_display_data = NodeDisplayData().dict()
                synthetic_node_label = "Final Output"
                nodes.append(
                    {
                        "id": str(final_output_node_id),
                        "type": "TERMINAL",
                        "data": {
                            "label": synthetic_node_label,
                            "name": workflow_output_display.name,
                            "target_handle_id": synthetic_target_handle_id,
                            "output_id": str(workflow_output_display.id),
                            "output_type": inferred_type,
                            "node_input_id": str(node_input.id),
                        },
                        "inputs": [node_input.dict()],
                        "display_data": synthetic_display_data,
                        "base": final_output_node_base,
                        "definition": None,
                    }
                )

                if source_node_display:
                    if isinstance(source_node_display, BaseNodeVellumDisplay):
                        source_handle_id = source_node_display.get_source_handle_id(
                            port_displays=self.display_context.port_displays
                        )
                    else:
                        source_handle_id = source_node_display.get_node_port_display(
                            source_node_display._node.Ports.default
                        ).id

                    synthetic_output_edges.append(
                        {
                            "id": str(uuid4_from_hash(f"{self.workflow_id}|edge_id|{workflow_output_display.name}")),
                            "source_node_id": str(source_node_display.node_id),
                            "source_handle_id": str(source_handle_id),
                            "target_node_id": str(final_output_node_id),
                            "target_handle_id": synthetic_target_handle_id,
                            "type": "DEFAULT",
                        }
                    )

            output_variables.append(
                {
                    "id": str(workflow_output_display.id),
                    "key": workflow_output_display.name,
                    "type": inferred_type,
                }
            )

        # If there are terminal nodes with no workflow output reference,
        # raise a serialization error
        if len(unreferenced_final_output_node_outputs) > 0:
            self.add_error(
                ValueError("Unable to serialize terminal nodes that are not referenced by workflow outputs.")
            )

        # Add an edge for each edge in the workflow
        for target_node, entrypoint_display in self.display_context.entrypoint_displays.items():
            unadorned_target_node = get_unadorned_node(target_node)
            target_node_display = self.display_context.node_displays[unadorned_target_node]
            edges.append(
                {
                    "id": str(entrypoint_display.edge_display.id),
                    "source_node_id": str(entrypoint_node_id),
                    "source_handle_id": str(entrypoint_node_source_handle_id),
                    "target_node_id": str(target_node_display.node_id),
                    "target_handle_id": str(target_node_display.get_trigger_id()),
                    "type": "DEFAULT",
                }
            )

        for (source_node_port, target_node), edge_display in self.display_context.edge_displays.items():
            unadorned_source_node_port = get_unadorned_port(source_node_port)
            unadorned_target_node = get_unadorned_node(target_node)

            source_node_port_display = self.display_context.port_displays[unadorned_source_node_port]
            target_node_display = self.display_context.node_displays[unadorned_target_node]

            edges.append(
                {
                    "id": str(edge_display.id),
                    "source_node_id": str(source_node_port_display.node_id),
                    "source_handle_id": str(source_node_port_display.id),
                    "target_node_id": str(target_node_display.node_id),
                    "target_handle_id": str(
                        target_node_display.get_target_handle_id_by_source_node_id(source_node_port_display.node_id)
                    ),
                    "type": "DEFAULT",
                }
            )

        edges.extend(synthetic_output_edges)

        return {
            "workflow_raw_data": {
                "nodes": nodes,
                "edges": edges,
                "display_data": self.display_context.workflow_display.display_data.dict(),
                "definition": {
                    "name": self._workflow.__name__,
                    "module": cast(JsonArray, self._workflow.__module__.split(".")),
                },
            },
            "input_variables": input_variables,
            "state_variables": state_variables,
            "output_variables": output_variables,
        }

    def _generate_workflow_input_display(
        self, workflow_input: WorkflowInputReference, overrides: Optional[WorkflowInputsVellumDisplayOverrides] = None
    ) -> WorkflowInputsVellumDisplay:
        workflow_input_id: UUID
        name = None
        required = None
        color = None
        if overrides:
            workflow_input_id = overrides.id
            name = overrides.name
            required = overrides.required
            color = overrides.color
        else:
            workflow_input_id = uuid4_from_hash(f"{self.workflow_id}|inputs|id|{workflow_input.name}")

        return WorkflowInputsVellumDisplay(id=workflow_input_id, name=name, required=required, color=color)
