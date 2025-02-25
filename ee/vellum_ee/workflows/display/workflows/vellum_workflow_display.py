import logging
from uuid import UUID
from typing import Dict, List, Optional, Type, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.edges import Edge
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.nodes.utils import get_unadorned_node, get_unadorned_port
from vellum.workflows.ports import Port
from vellum.workflows.references import WorkflowInputReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplay
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type
from vellum_ee.workflows.display.vellum import (
    EdgeVellumDisplay,
    EdgeVellumDisplayOverrides,
    EntrypointVellumDisplay,
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    StateValueVellumDisplay,
    StateValueVellumDisplayOverrides,
    WorkflowInputsVellumDisplay,
    WorkflowInputsVellumDisplayOverrides,
    WorkflowMetaVellumDisplay,
    WorkflowMetaVellumDisplayOverrides,
)
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay

logger = logging.getLogger(__name__)


class VellumWorkflowDisplay(
    BaseWorkflowDisplay[
        WorkflowType,
        WorkflowMetaVellumDisplay,
        WorkflowMetaVellumDisplayOverrides,
        WorkflowInputsVellumDisplay,
        WorkflowInputsVellumDisplayOverrides,
        StateValueVellumDisplay,
        StateValueVellumDisplayOverrides,
        BaseNodeDisplay,
        EntrypointVellumDisplay,
        EntrypointVellumDisplayOverrides,
        EdgeVellumDisplay,
        EdgeVellumDisplayOverrides,
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
        for state_value, state_value_display in self.display_context.state_value_displays.items():
            default = primitive_to_vellum_value(state_value.instance) if state_value.instance else None
            required = (
                state_value_display.required
                if state_value_display.required is not None
                else type(None) not in state_value.types
            )
            state_variables.append(
                {
                    "id": str(state_value_display.id),
                    "key": state_value_display.name or state_value.name,
                    "type": infer_vellum_variable_type(state_value),
                    "default": default.dict() if default else None,
                    "required": required,
                    "extensions": {"color": state_value_display.color},
                }
            )

        nodes: JsonArray = []
        edges: JsonArray = []

        # Add a single synthetic node for the workflow entrypoint
        nodes.append(
            {
                "id": str(self.display_context.workflow_display.entrypoint_node_id),
                "type": "ENTRYPOINT",
                "inputs": [],
                "data": {
                    "label": "Entrypoint Node",
                    "source_handle_id": str(self.display_context.workflow_display.entrypoint_node_source_handle_id),
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
        all_edge_displays: List[EdgeVellumDisplay] = [
            # Create a synthetic edge from the synthetic entrypoint node to each actual entrypoint
            *[
                entrypoint_display.edge_display
                for entrypoint_display in self.display_context.entrypoint_displays.values()
            ],
            # Include the concrete edges in the workflow
            *self.display_context.edge_displays.values(),
        ]

        for edge_display in all_edge_displays:
            edges.append(
                {
                    "id": str(edge_display.id),
                    "source_node_id": str(edge_display.source_node_id),
                    "source_handle_id": str(edge_display.source_handle_id),
                    "target_node_id": str(edge_display.target_node_id),
                    "target_handle_id": str(edge_display.target_handle_id),
                    "type": edge_display.type,
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

    def _generate_workflow_meta_display(self) -> WorkflowMetaVellumDisplay:
        overrides = self.workflow_display
        if overrides:
            return WorkflowMetaVellumDisplay(
                entrypoint_node_id=overrides.entrypoint_node_id,
                entrypoint_node_source_handle_id=overrides.entrypoint_node_source_handle_id,
                entrypoint_node_display=overrides.entrypoint_node_display,
                display_data=overrides.display_data,
            )

        entrypoint_node_id = uuid4_from_hash(f"{self.workflow_id}|entrypoint_node_id")
        entrypoint_node_source_handle_id = uuid4_from_hash(f"{self.workflow_id}|entrypoint_node_source_handle_id")

        return WorkflowMetaVellumDisplay(
            entrypoint_node_id=entrypoint_node_id,
            entrypoint_node_source_handle_id=entrypoint_node_source_handle_id,
            entrypoint_node_display=NodeDisplayData(),
        )

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

    def _generate_state_value_display(
        self, state_value: BaseDescriptor, overrides: Optional[StateValueVellumDisplayOverrides] = None
    ) -> StateValueVellumDisplay:
        state_value_id: UUID
        name = None
        required = None
        color = None
        if overrides:
            state_value_id = overrides.id
            name = overrides.name
            required = overrides.required
            color = overrides.color
        else:
            state_value_id = uuid4_from_hash(f"{self.workflow_id}|state_values|id|{state_value.name}")

        return StateValueVellumDisplay(id=state_value_id, name=name, required=required, color=color)

    def _generate_entrypoint_display(
        self,
        entrypoint: Type[BaseNode],
        workflow_display: WorkflowMetaVellumDisplay,
        node_displays: Dict[Type[BaseNode], BaseNodeDisplay],
        overrides: Optional[EntrypointVellumDisplayOverrides] = None,
    ) -> EntrypointVellumDisplay:
        entrypoint_node_id = workflow_display.entrypoint_node_id
        source_handle_id = workflow_display.entrypoint_node_source_handle_id

        edge_display_overrides = overrides.edge_display if overrides else None
        entrypoint_id = (
            edge_display_overrides.id
            if edge_display_overrides
            else uuid4_from_hash(f"{self.workflow_id}|id|{entrypoint_node_id}")
        )

        entrypoint_target = get_unadorned_node(entrypoint)
        target_node_display = node_displays[entrypoint_target]
        target_node_id = target_node_display.node_id
        if isinstance(target_node_display, BaseNodeVellumDisplay):
            target_handle_id = target_node_display.get_target_handle_id_by_source_node_id(entrypoint_node_id)
        else:
            target_handle_id = target_node_display.get_trigger_id()

        edge_display = self._generate_edge_display_from_source(
            entrypoint_node_id, source_handle_id, target_node_id, target_handle_id, overrides=edge_display_overrides
        )

        return EntrypointVellumDisplay(id=entrypoint_id, edge_display=edge_display)

    def _generate_edge_display(
        self,
        edge: Edge,
        node_displays: Dict[Type[BaseNode], BaseNodeDisplay],
        port_displays: Dict[Port, PortDisplay],
        overrides: Optional[EdgeVellumDisplayOverrides] = None,
    ) -> EdgeVellumDisplay:
        source_node = get_unadorned_node(edge.from_port.node_class)
        target_node = get_unadorned_node(edge.to_node)

        source_node_id = node_displays[source_node].node_id
        from_port = get_unadorned_port(edge.from_port)
        source_handle_id = port_displays[from_port].id

        target_node_display = node_displays[target_node]
        target_node_id = target_node_display.node_id

        if isinstance(target_node_display, BaseNodeVellumDisplay):
            target_handle_id = target_node_display.get_target_handle_id_by_source_node_id(source_node_id)
        else:
            target_handle_id = target_node_display.get_trigger_id()

        return self._generate_edge_display_from_source(
            source_node_id, source_handle_id, target_node_id, target_handle_id, overrides
        )

    def _generate_edge_display_from_source(
        self,
        source_node_id: UUID,
        source_handle_id: UUID,
        target_node_id: UUID,
        target_handle_id: UUID,
        overrides: Optional[EdgeVellumDisplayOverrides] = None,
    ) -> EdgeVellumDisplay:
        edge_id: UUID
        if overrides:
            edge_id = overrides.id
        else:
            edge_id = uuid4_from_hash(f"{self.workflow_id}|id|{source_node_id}|{target_node_id}")

        return EdgeVellumDisplay(
            id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            source_handle_id=source_handle_id,
            target_handle_id=target_handle_id,
        )
