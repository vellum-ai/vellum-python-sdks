import logging
from uuid import UUID
from typing import Dict, List, Optional, Type, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.edges import Edge
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.nodes.utils import get_unadorned_node, get_unadorned_port, get_wrapped_node, has_wrapped_node
from vellum.workflows.ports import Port
from vellum.workflows.references import WorkflowInputReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplay
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type, primitive_to_vellum_value
from vellum_ee.workflows.display.vellum import (
    EdgeVellumDisplay,
    EdgeVellumDisplayOverrides,
    EntrypointVellumDisplay,
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    WorkflowInputsVellumDisplay,
    WorkflowInputsVellumDisplayOverrides,
    WorkflowMetaVellumDisplay,
    WorkflowMetaVellumDisplayOverrides,
    WorkflowOutputVellumDisplay,
    WorkflowOutputVellumDisplayOverrides,
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
        BaseNodeVellumDisplay,
        EntrypointVellumDisplay,
        EntrypointVellumDisplayOverrides,
        EdgeVellumDisplay,
        EdgeVellumDisplayOverrides,
        WorkflowOutputVellumDisplay,
        WorkflowOutputVellumDisplayOverrides,
    ]
):
    node_display_base_class = BaseNodeVellumDisplay

    def serialize(self, raise_errors: bool = True) -> JsonObject:
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

        nodes: JsonArray = []
        edges: JsonArray = []

        # Add a single synthetic node for the workflow entrypoint
        base_node_definition: JsonObject = {
            "name": BaseNode.__name__,
            "module": cast(JsonArray, BaseNode.__module__.split(".")),
            "bases": [],
        }
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
                "definition": base_node_definition,
            },
        )

        # Add all the nodes in the workflow
        for node, node_display in self.display_context.node_displays.items():
            if getattr(node, "_is_wrapped_node") is True:
                # Nodes that are wrapped or decorated by other nodes are not serialized here
                # They are instead serialized by the wrapper node
                continue

            try:
                serialized_node = node_display.serialize(self.display_context)
            except NotImplementedError:
                logger.warning("Unable to serialize node", extra={"node": node.__name__})
                if raise_errors:
                    raise
                else:
                    continue

            nodes.append(serialized_node)

        synthetic_output_edges: JsonArray = []
        output_variables: JsonArray = []
        final_output_nodes = [
            node for node in self.display_context.node_displays.keys() if issubclass(node, FinalOutputNode)
        ]
        final_output_node_outputs = {node.Outputs.value for node in final_output_nodes}
        unreferenced_final_output_node_outputs = final_output_node_outputs.copy()
        final_output_node_definition: JsonObject = {
            "name": FinalOutputNode.__name__,
            "module": cast(JsonArray, FinalOutputNode.__module__.split(".")),
            "bases": [base_node_definition],
        }

        # Add a synthetic Terminal Node and track the Workflow's output variables for each Workflow output
        for workflow_output, workflow_output_display in self.display_context.workflow_output_displays.items():
            final_output_node_id = workflow_output_display.node_id
            inferred_type = infer_vellum_variable_type(workflow_output)

            # Remove the terminal node output from the unreferenced set
            unreferenced_final_output_node_outputs.discard(cast(OutputReference, workflow_output.instance))

            if workflow_output.instance not in final_output_node_outputs:
                # Create a synthetic terminal node only if there is no terminal node for this output
                node_input = create_node_input(
                    final_output_node_id,
                    "node_input",
                    # This is currently the wrapper node's output, but we want the wrapped node
                    workflow_output.instance,
                    self.display_context,
                    workflow_output_display.node_input_id,
                )

                source_node_display: Optional[BaseNodeVellumDisplay]
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

                nodes.append(
                    {
                        "id": str(final_output_node_id),
                        "type": "TERMINAL",
                        "data": {
                            "label": workflow_output_display.label,
                            "name": workflow_output_display.name,
                            "target_handle_id": str(workflow_output_display.target_handle_id),
                            "output_id": str(workflow_output_display.id),
                            "output_type": inferred_type,
                            "node_input_id": str(node_input.id),
                        },
                        "inputs": [node_input.dict()],
                        "display_data": workflow_output_display.display_data.dict(),
                        "definition": final_output_node_definition,
                    }
                )

                if source_node_display:
                    synthetic_output_edges.append(
                        {
                            "id": str(workflow_output_display.edge_id),
                            "source_node_id": str(source_node_display.node_id),
                            "source_handle_id": str(
                                source_node_display.get_source_handle_id(
                                    port_displays=self.display_context.port_displays
                                )
                            ),
                            "target_node_id": str(workflow_output_display.node_id),
                            "target_handle_id": str(workflow_output_display.target_handle_id),
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
            raise ValueError("Unable to serialize terminal nodes that are not referenced by workflow outputs.")

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
        required = None
        color = None
        if overrides:
            workflow_input_id = overrides.id
            required = overrides.required
            color = overrides.color
        else:
            workflow_input_id = uuid4_from_hash(f"{self.workflow_id}|inputs|id|{workflow_input.name}")

        return WorkflowInputsVellumDisplay(id=workflow_input_id, required=required, color=color)

    def _generate_entrypoint_display(
        self,
        entrypoint: Type[BaseNode],
        workflow_display: WorkflowMetaVellumDisplay,
        node_displays: Dict[Type[BaseNode], BaseNodeVellumDisplay],
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

        if has_wrapped_node(entrypoint):
            wrapped_node = get_wrapped_node(entrypoint)
            if wrapped_node._is_wrapped_node:
                entrypoint = wrapped_node

        target_node_id = node_displays[entrypoint].node_id
        target_handle_id = node_displays[entrypoint].get_target_handle_id()

        edge_display = self._generate_edge_display_from_source(
            entrypoint_node_id, source_handle_id, target_node_id, target_handle_id, overrides=edge_display_overrides
        )

        return EntrypointVellumDisplay(id=entrypoint_id, edge_display=edge_display)

    def _generate_workflow_output_display(
        self,
        output: BaseDescriptor,
        overrides: Optional[WorkflowOutputVellumDisplayOverrides] = None,
    ) -> WorkflowOutputVellumDisplay:
        if overrides:
            return WorkflowOutputVellumDisplay(
                id=overrides.id,
                name=overrides.name,
                label=overrides.label,
                node_id=overrides.node_id,
                node_input_id=overrides.node_input_id,
                target_handle_id=overrides.target_handle_id,
                edge_id=overrides.edge_id,
                display_data=overrides.display_data,
            )

        output_id = uuid4_from_hash(f"{self.workflow_id}|id|{output.name}")
        edge_id = uuid4_from_hash(f"{self.workflow_id}|edge_id|{output.name}")
        node_id = uuid4_from_hash(f"{self.workflow_id}|node_id|{output.name}")
        node_input_id = uuid4_from_hash(f"{self.workflow_id}|node_input_id|{output.name}")
        target_handle_id = uuid4_from_hash(f"{self.workflow_id}|target_handle_id|{output.name}")

        return WorkflowOutputVellumDisplay(
            id=output_id,
            node_id=node_id,
            node_input_id=node_input_id,
            name=output.name,
            label="Final Output",
            target_handle_id=target_handle_id,
            edge_id=edge_id,
            display_data=NodeDisplayData(),
        )

    def _generate_edge_display(
        self,
        edge: Edge,
        node_displays: Dict[Type[BaseNode], BaseNodeVellumDisplay],
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

        target_handle_id: UUID
        target_handle_id = target_node_display.get_target_handle_id_by_source_node_id(source_node_id)

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
