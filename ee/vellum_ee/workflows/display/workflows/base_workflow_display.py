from copy import copy
import fnmatch
from functools import cached_property
import importlib
import inspect
import json
import logging
import os
from uuid import UUID
from typing import Any, Dict, ForwardRef, Generic, List, Optional, Tuple, Type, TypeVar, Union, cast, get_args

from vellum.client import Vellum as VellumClient
from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.edges import Edge
from vellum.workflows.events.workflow import NodeEventDisplayContext, WorkflowEventDisplayContext
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.nodes.utils import get_unadorned_node, get_unadorned_port, get_wrapped_node
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, WorkflowInputReference
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.core import Json, JsonArray, JsonObject
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.vellum_client import create_vellum_client
from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    StateValueDisplay,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.exceptions import NodeValidationError
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import (
    EdgeDisplays,
    EntrypointDisplays,
    NodeDisplays,
    NodeOutputDisplays,
    PortDisplays,
    StateValueDisplays,
    WorkflowDisplayContext,
    WorkflowInputsDisplays,
    WorkflowOutputDisplays,
)
from vellum_ee.workflows.display.utils.auto_layout import auto_layout_nodes
from vellum_ee.workflows.display.utils.expressions import serialize_value
from vellum_ee.workflows.display.utils.registry import register_workflow_display_class
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

logger = logging.getLogger(__name__)

IGNORE_PATTERNS = [
    "*.pyc",
    "__pycache__",
    ".*",
    "node_modules/*",
    "*.log",
]


class WorkflowSerializationResult(UniversalBaseModel):
    exec_config: Dict[str, Any]
    errors: List[str]
    dataset: Optional[List[Dict[str, Any]]] = None


class BaseWorkflowDisplay(Generic[WorkflowType]):
    # Used to specify the display data for a workflow.
    workflow_display: Optional[WorkflowMetaDisplay] = None

    # Used to explicitly specify display data for a workflow's inputs.
    inputs_display: WorkflowInputsDisplays = {}

    # Used to explicitly specify display data for a workflow's state values.
    state_value_displays: StateValueDisplays = {}

    # Used to explicitly specify display data for a workflow's entrypoints.
    entrypoint_displays: EntrypointDisplays = {}

    # Used to explicitly specify display data for a workflow's outputs.
    output_displays: WorkflowOutputDisplays = {}

    # Used to explicitly specify display data for a workflow's edges.
    edge_displays: EdgeDisplays = {}

    # Used to explicitly specify display data for a workflow's ports.
    port_displays: PortDisplays = {}

    _serialized_files: List[str]

    _dry_run: bool

    def __init__(
        self,
        *,
        parent_display_context: Optional[WorkflowDisplayContext] = None,
        client: Optional[VellumClient] = None,
        dry_run: bool = False,
    ):
        self._parent_display_context = parent_display_context
        self._client = client or (
            # propagate the client from the parent display context if it is not provided
            self._parent_display_context.client
            if self._parent_display_context
            else create_vellum_client()
        )
        self._serialized_files = []
        self._dry_run = dry_run

    def serialize(self) -> JsonObject:
        self._serialized_files = [
            "__init__.py",
            "display/*",
            "inputs.py",
            "nodes/*",
            "state.py",
            "workflow.py",
        ]

        input_variables: JsonArray = []
        for workflow_input_reference, workflow_input_display in self.display_context.workflow_input_displays.items():
            default = (
                primitive_to_vellum_value(workflow_input_reference.instance)
                if workflow_input_reference.instance
                else None
            )

            is_required = self._is_reference_required(workflow_input_reference)

            input_variables.append(
                {
                    "id": str(workflow_input_display.id),
                    "key": workflow_input_display.name or workflow_input_reference.name,
                    "type": infer_vellum_variable_type(workflow_input_reference),
                    "default": default.dict() if default else None,
                    "required": is_required,
                    "extensions": {"color": workflow_input_display.color},
                }
            )

        state_variables: JsonArray = []
        for state_value_reference, state_value_display in self.display_context.state_value_displays.items():
            default = (
                primitive_to_vellum_value(state_value_reference.instance) if state_value_reference.instance else None
            )

            is_required = self._is_reference_required(state_value_reference)

            state_variables.append(
                {
                    "id": str(state_value_display.id),
                    "key": state_value_display.name or state_value_reference.name,
                    "type": infer_vellum_variable_type(state_value_reference),
                    "default": default.dict() if default else None,
                    "required": is_required,
                    "extensions": {"color": state_value_display.color},
                }
            )

        serialized_nodes: Dict[UUID, JsonObject] = {}
        edges: JsonArray = []

        # Add a single synthetic node for the workflow entrypoint
        entrypoint_node_id = self.display_context.workflow_display.entrypoint_node_id
        entrypoint_node_source_handle_id = self.display_context.workflow_display.entrypoint_node_source_handle_id
        serialized_nodes[entrypoint_node_id] = {
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
        }

        # Add all the nodes in the workflows
        for node in self._workflow.get_all_nodes():
            node_display = self.display_context.node_displays[node]

            try:
                serialized_node = node_display.serialize(self.display_context)
            except (NotImplementedError, NodeValidationError) as e:
                self.display_context.add_error(e)
                self.display_context.add_invalid_node(node)
                continue

            serialized_nodes[node_display.node_id] = serialized_node

        synthetic_output_edges: JsonArray = []
        output_variables: JsonArray = []
        output_values: JsonArray = []
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
            if isinstance(workflow_output.instance, OutputReference):
                unreferenced_final_output_node_outputs.discard(workflow_output.instance)

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
                if not node_input.value.rules:
                    source_node_display = None
                else:
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
                    else:
                        source_node_display = None

                synthetic_target_handle_id = str(
                    uuid4_from_hash(f"{self.workflow_id}|target_handle_id|{workflow_output_display.name}")
                )
                synthetic_display_data = NodeDisplayData().dict()
                synthetic_node_label = "Final Output"
                serialized_nodes[final_output_node_id] = {
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

                if source_node_display:
                    source_handle_id = source_node_display.get_source_handle_id(
                        port_displays=self.display_context.port_displays
                    )

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

            elif isinstance(workflow_output.instance, OutputReference):
                terminal_node_id = workflow_output.instance.outputs_class.__parent_class__.__id__
                serialized_terminal_node = serialized_nodes.get(terminal_node_id)
                if serialized_terminal_node and isinstance(serialized_terminal_node["data"], dict):
                    serialized_terminal_node["data"]["name"] = workflow_output_display.name

            output_values.append(
                {
                    "output_variable_id": str(workflow_output_display.id),
                    "value": serialize_value(self.display_context, workflow_output.instance),
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
            self.display_context.add_error(
                ValueError("Unable to serialize terminal nodes that are not referenced by workflow outputs.")
            )

        # Add an edge for each edge in the workflow
        for target_node, entrypoint_display in self.display_context.entrypoint_displays.items():
            unadorned_target_node = get_unadorned_node(target_node)
            # Skip edges to invalid nodes
            if self._is_node_invalid(unadorned_target_node):
                continue

            target_node_display = self.display_context.node_displays[unadorned_target_node]
            entrypoint_edge_dict: Dict[str, Json] = {
                "id": str(entrypoint_display.edge_display.id),
                "source_node_id": str(entrypoint_node_id),
                "source_handle_id": str(entrypoint_node_source_handle_id),
                "target_node_id": str(target_node_display.node_id),
                "target_handle_id": str(target_node_display.get_trigger_id()),
                "type": "DEFAULT",
            }
            display_data = self._serialize_edge_display_data(entrypoint_display.edge_display)
            if display_data is not None:
                entrypoint_edge_dict["display_data"] = display_data
            edges.append(entrypoint_edge_dict)

        for (source_node_port, target_node), edge_display in self.display_context.edge_displays.items():
            unadorned_source_node_port = get_unadorned_port(source_node_port)
            unadorned_target_node = get_unadorned_node(target_node)

            # Skip edges that reference invalid nodes
            if self._is_node_invalid(unadorned_target_node) or self._is_node_invalid(
                unadorned_source_node_port.node_class
            ):
                continue

            source_node_port_display = self.display_context.port_displays[unadorned_source_node_port]
            target_node_display = self.display_context.node_displays[unadorned_target_node]

            regular_edge_dict: Dict[str, Json] = {
                "id": str(edge_display.id),
                "source_node_id": str(source_node_port_display.node_id),
                "source_handle_id": str(source_node_port_display.id),
                "target_node_id": str(target_node_display.node_id),
                "target_handle_id": str(
                    target_node_display.get_target_handle_id_by_source_node_id(source_node_port_display.node_id)
                ),
                "type": "DEFAULT",
            }
            display_data = self._serialize_edge_display_data(edge_display)
            if display_data is not None:
                regular_edge_dict["display_data"] = display_data
            edges.append(regular_edge_dict)

        edges.extend(synthetic_output_edges)

        nodes_list = list(serialized_nodes.values())
        nodes_dict_list = [cast(Dict[str, Any], node) for node in nodes_list if isinstance(node, dict)]

        all_nodes_at_zero = all(
            (
                isinstance(node.get("display_data"), dict)
                and isinstance(node["display_data"].get("position"), dict)
                and node["display_data"]["position"].get("x", 0) == 0.0
                and node["display_data"]["position"].get("y", 0) == 0.0
            )
            for node in nodes_dict_list
        )

        should_apply_auto_layout = all_nodes_at_zero and len(nodes_dict_list) > 0

        if should_apply_auto_layout:
            try:
                self._apply_auto_layout(nodes_dict_list, edges)
            except Exception as e:
                self.display_context.add_error(e)

        return {
            "workflow_raw_data": {
                "nodes": cast(JsonArray, nodes_dict_list),
                "edges": edges,
                "display_data": self.display_context.workflow_display.display_data.dict(),
                "definition": {
                    "name": self._workflow.__name__,
                    "module": cast(JsonArray, self._workflow.__module__.split(".")),
                },
                "output_values": output_values,
            },
            "input_variables": input_variables,
            "state_variables": state_variables,
            "output_variables": output_variables,
        }

    def _serialize_edge_display_data(self, edge_display: EdgeDisplay) -> Optional[JsonObject]:
        """Serialize edge display data, returning None if no display data is present."""
        if edge_display.z_index is not None:
            return {"z_index": edge_display.z_index}
        return None

    def _apply_auto_layout(self, nodes_dict_list: List[Dict[str, Any]], edges: List[Json]) -> None:
        """Apply auto-layout to nodes that are all positioned at (0,0)."""
        nodes_for_layout: List[Tuple[str, NodeDisplayData]] = []
        for node_dict in nodes_dict_list:
            if isinstance(node_dict.get("id"), str) and isinstance(node_dict.get("display_data"), dict):
                display_data = node_dict["display_data"]
                position = display_data.get("position", {})
                if isinstance(position, dict):
                    nodes_for_layout.append(
                        (
                            str(node_dict["id"]),
                            NodeDisplayData(
                                position=NodeDisplayPosition(
                                    x=float(position.get("x", 0.0)), y=float(position.get("y", 0.0))
                                ),
                                width=display_data.get("width"),
                                height=display_data.get("height"),
                                comment=display_data.get("comment"),
                            ),
                        )
                    )

        edges_for_layout: List[Tuple[str, str, EdgeDisplay]] = []
        for edge in edges:
            if isinstance(edge, dict):
                edge_dict = cast(Dict[str, Any], edge)
                edge_source_node_id: Optional[Any] = edge_dict.get("source_node_id")
                edge_target_node_id: Optional[Any] = edge_dict.get("target_node_id")
                edge_id_raw: Optional[Any] = edge_dict.get("id")
                if (
                    isinstance(edge_source_node_id, str)
                    and isinstance(edge_target_node_id, str)
                    and isinstance(edge_id_raw, str)
                ):
                    edges_for_layout.append(
                        (edge_source_node_id, edge_target_node_id, EdgeDisplay(id=UUID(edge_id_raw)))
                    )

        positioned_nodes = auto_layout_nodes(nodes_for_layout, edges_for_layout)

        for node_id, positioned_data in positioned_nodes:
            for node_dict in nodes_dict_list:
                node_id_val = node_dict.get("id")
                display_data = node_dict.get("display_data")
                if isinstance(node_id_val, str) and node_id_val == node_id and isinstance(display_data, dict):
                    display_data_dict = cast(Dict[str, Any], display_data)
                    display_data_dict["position"] = positioned_data.position.dict()

    @cached_property
    def workflow_id(self) -> UUID:
        """Can be overridden as a class attribute to specify a custom workflow id."""
        return self._workflow.__id__

    def _enrich_global_node_output_displays(
        self,
        node: Type[BaseNode],
        node_display: BaseNodeDisplay,
        node_output_displays: Dict[OutputReference, Tuple[Type[BaseNode], NodeOutputDisplay]],
    ):
        """This method recursively adds nodes wrapped in decorators to the node_output_displays dictionary."""

        inner_node = get_wrapped_node(node)
        if inner_node:
            inner_node_display = self._get_node_display(inner_node)
            self._enrich_global_node_output_displays(inner_node, inner_node_display, node_output_displays)

        for node_output in node.Outputs:
            if node_output in node_output_displays:
                continue

            node_output_displays[node_output] = node_display.get_node_output_display(node_output)

    def _enrich_node_port_displays(
        self,
        node: Type[BaseNode],
        node_display: BaseNodeDisplay,
        port_displays: Dict[Port, PortDisplay],
    ):
        """This method recursively adds nodes wrapped in decorators to the port_displays dictionary."""

        inner_node = get_wrapped_node(node)
        if inner_node:
            inner_node_display = self._get_node_display(inner_node)
            self._enrich_node_port_displays(inner_node, inner_node_display, port_displays)

        for port in node.Ports:
            if port in port_displays:
                continue

            port_displays[port] = node_display.get_node_port_display(port)

    def _get_node_display(self, node: Type[BaseNode]) -> BaseNodeDisplay:
        node_display_class = get_node_display_class(node)
        return node_display_class()

    @cached_property
    def display_context(self) -> WorkflowDisplayContext:
        workflow_meta_display = self._generate_workflow_meta_display()

        global_node_output_displays: NodeOutputDisplays = (
            copy(self._parent_display_context.global_node_output_displays) if self._parent_display_context else {}
        )

        node_displays: NodeDisplays = {}

        global_node_displays: NodeDisplays = (
            copy(self._parent_display_context.global_node_displays) if self._parent_display_context else {}
        )

        port_displays: PortDisplays = {}

        for node in self._workflow.get_all_nodes():
            self._enrich_node_displays(
                node=node,
                node_displays=node_displays,
                global_node_displays=global_node_displays,
                global_node_output_displays=global_node_output_displays,
                port_displays=port_displays,
            )

        workflow_input_displays: WorkflowInputsDisplays = {}
        # If we're dealing with a nested workflow, then it should have access to the inputs of its parents.
        global_workflow_input_displays = (
            copy(self._parent_display_context.global_workflow_input_displays) if self._parent_display_context else {}
        )
        for workflow_input in self._workflow.get_inputs_class():
            workflow_input_display_overrides = self.inputs_display.get(workflow_input)
            input_display = self._generate_workflow_input_display(
                workflow_input, overrides=workflow_input_display_overrides
            )
            workflow_input_displays[workflow_input] = input_display
            global_workflow_input_displays[workflow_input] = input_display

        state_value_displays: StateValueDisplays = {}
        global_state_value_displays = (
            copy(self._parent_display_context.global_state_value_displays) if self._parent_display_context else {}
        )
        for state_value in self._workflow.get_state_class():
            state_value_display_overrides = self.state_value_displays.get(state_value)
            state_value_display = self._generate_state_value_display(
                state_value, overrides=state_value_display_overrides
            )
            state_value_displays[state_value] = state_value_display
            global_state_value_displays[state_value] = state_value_display

        entrypoint_displays: EntrypointDisplays = {}
        for entrypoint in self._workflow.get_entrypoints():
            if entrypoint in entrypoint_displays:
                continue

            entrypoint_display_overrides = self.entrypoint_displays.get(entrypoint)
            entrypoint_displays[entrypoint] = self._generate_entrypoint_display(
                entrypoint, workflow_meta_display, node_displays, overrides=entrypoint_display_overrides
            )

        edge_displays: Dict[Tuple[Port, Type[BaseNode]], EdgeDisplay] = {}
        for edge in self._workflow.get_edges():
            if edge in edge_displays:
                continue

            edge_display_overrides = self.edge_displays.get((edge.from_port, edge.to_node))
            edge_displays[(edge.from_port, edge.to_node)] = edge_display_overrides or self._generate_edge_display(
                edge, node_displays
            )

        for edge in self._workflow.get_unused_edges():
            if edge in edge_displays:
                continue

            edge_display_overrides = self.edge_displays.get((edge.from_port, edge.to_node))
            edge_displays[(edge.from_port, edge.to_node)] = edge_display_overrides or self._generate_edge_display(
                edge, node_displays
            )

        workflow_output_displays: Dict[BaseDescriptor, WorkflowOutputDisplay] = {}
        for workflow_output in self._workflow.Outputs:
            if workflow_output in workflow_output_displays:
                continue

            if not isinstance(workflow_output, OutputReference):
                raise ValueError(f"{workflow_output} must be an {OutputReference.__name__}")

            workflow_output_display = self.output_displays.get(workflow_output)
            workflow_output_displays[workflow_output] = (
                workflow_output_display or self._generate_workflow_output_display(workflow_output, self._workflow)
            )

        return WorkflowDisplayContext(
            client=self._client,
            workflow_display=workflow_meta_display,
            workflow_input_displays=workflow_input_displays,
            global_workflow_input_displays=global_workflow_input_displays,
            state_value_displays=state_value_displays,
            global_state_value_displays=global_state_value_displays,
            node_displays=node_displays,
            global_node_output_displays=global_node_output_displays,
            global_node_displays=global_node_displays,
            entrypoint_displays=entrypoint_displays,
            workflow_output_displays=workflow_output_displays,
            edge_displays=edge_displays,
            port_displays=port_displays,
            workflow_display_class=self.__class__,
            _dry_run=self._dry_run,
        )

    def _generate_workflow_meta_display(self) -> WorkflowMetaDisplay:
        overrides = self.workflow_display
        if overrides:
            return WorkflowMetaDisplay(
                entrypoint_node_id=overrides.entrypoint_node_id,
                entrypoint_node_source_handle_id=overrides.entrypoint_node_source_handle_id,
                entrypoint_node_display=overrides.entrypoint_node_display,
                display_data=overrides.display_data,
            )

        return WorkflowMetaDisplay.get_default(self._workflow)

    def _generate_workflow_input_display(
        self, workflow_input: WorkflowInputReference, overrides: Optional[WorkflowInputsDisplay] = None
    ) -> WorkflowInputsDisplay:
        workflow_input_id: UUID
        name = None
        color = None
        if overrides:
            workflow_input_id = overrides.id
            name = overrides.name
            color = overrides.color
        else:
            workflow_input_id = uuid4_from_hash(f"{self.workflow_id}|inputs|id|{workflow_input.name}")

        return WorkflowInputsDisplay(id=workflow_input_id, name=name, color=color)

    def _generate_state_value_display(
        self, state_value: BaseDescriptor, overrides: Optional[StateValueDisplay] = None
    ) -> StateValueDisplay:
        state_value_id: UUID
        name = None
        color = None
        if overrides:
            state_value_id = overrides.id
            name = overrides.name
            color = overrides.color
        else:
            state_value_id = uuid4_from_hash(f"{self.workflow_id}|state_values|id|{state_value.name}")

        return StateValueDisplay(id=state_value_id, name=name, color=color)

    def _generate_entrypoint_display(
        self,
        entrypoint: Type[BaseNode],
        workflow_display: WorkflowMetaDisplay,
        node_displays: Dict[Type[BaseNode], BaseNodeDisplay],
        overrides: Optional[EntrypointDisplay] = None,
    ) -> EntrypointDisplay:
        entrypoint_node_id = workflow_display.entrypoint_node_id

        edge_display_overrides = overrides.edge_display if overrides else None
        entrypoint_id = (
            edge_display_overrides.id
            if edge_display_overrides
            else uuid4_from_hash(f"{self.workflow_id}|id|{entrypoint_node_id}")
        )

        entrypoint_target = get_unadorned_node(entrypoint)
        target_node_display = node_displays[entrypoint_target]
        target_node_id = target_node_display.node_id

        edge_display = edge_display_overrides or self._generate_edge_display_from_source(
            entrypoint_node_id, target_node_id
        )

        return EntrypointDisplay(id=entrypoint_id, edge_display=edge_display)

    def _generate_workflow_output_display(
        self, output: OutputReference, workflow_class: Type[BaseWorkflow]
    ) -> WorkflowOutputDisplay:
        # TODO: use the output.id field instead once we add `__parent_class__` to BaseWorkflow.Outputs
        output_id = workflow_class.__output_ids__.get(output.name) or uuid4_from_hash(
            f"{self.workflow_id}|id|{output.name}"
        )
        return WorkflowOutputDisplay(id=output_id, name=output.name)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        workflow_class = get_args(cls.__orig_bases__[0])[0]  # type: ignore [attr-defined]
        register_workflow_display_class(workflow_class=workflow_class, workflow_display_class=cls)

    @staticmethod
    def gather_event_display_context(
        module_path: str,
        # DEPRECATED: This will be removed in the 0.15.0 release
        workflow_class: Optional[Type[BaseWorkflow]] = None,
    ) -> Union[WorkflowEventDisplayContext, None]:
        full_workflow_display_module_path = f"{module_path}.display.workflow"
        try:
            display_module = importlib.import_module(full_workflow_display_module_path)
        except ModuleNotFoundError:
            return BaseWorkflowDisplay._gather_event_display_context_from_workflow_crawling(module_path, workflow_class)

        WorkflowDisplayClass: Optional[Type[BaseWorkflowDisplay]] = None
        for name, definition in display_module.__dict__.items():
            if name.startswith("_"):
                continue

            if (
                not isinstance(definition, type)
                or not issubclass(definition, BaseWorkflowDisplay)
                or definition == BaseWorkflowDisplay
            ):
                continue

            WorkflowDisplayClass = definition
            break

        if WorkflowDisplayClass:
            return WorkflowDisplayClass().get_event_display_context()

        return BaseWorkflowDisplay._gather_event_display_context_from_workflow_crawling(module_path, workflow_class)

    @staticmethod
    def _gather_event_display_context_from_workflow_crawling(
        module_path: str,
        workflow_class: Optional[Type[BaseWorkflow]] = None,
    ) -> Union[WorkflowEventDisplayContext, None]:
        try:
            if workflow_class is None:
                workflow_class = BaseWorkflow.load_from_module(module_path)

            workflow_display = get_workflow_display(workflow_class=workflow_class)
            return workflow_display.get_event_display_context()

        except ModuleNotFoundError:
            logger.exception("Failed to load workflow from module %s", module_path)
            return None

    def get_event_display_context(self):
        display_context = self.display_context

        workflow_outputs = {
            output.name: display_context.workflow_output_displays[output].id
            for output in display_context.workflow_output_displays
        }
        workflow_inputs = {
            input.name: display_context.workflow_input_displays[input].id
            for input in display_context.workflow_input_displays
        }
        node_displays = {
            node.__id__: (node, display_context.node_displays[node]) for node in display_context.node_displays
        }
        node_event_displays = {}
        for node_id in node_displays:
            node, current_node_display = node_displays[node_id]
            input_display = current_node_display.node_input_ids_by_name
            output_display = {
                output.name: current_node_display.output_display[output].id
                for output in current_node_display.output_display
            }
            port_display_meta = {
                port.name: current_node_display.port_displays[port].id for port in current_node_display.port_displays
            }
            subworkflow_display_context: Optional[WorkflowEventDisplayContext] = None
            if hasattr(node, "subworkflow"):
                # All nodes that have a subworkflow attribute are currently expected to call them `subworkflow`
                # This will change if in the future we decide to support multiple subworkflows on a single node
                subworkflow_attribute = raise_if_descriptor(getattr(node, "subworkflow"))
                if issubclass(subworkflow_attribute, BaseWorkflow):
                    subworkflow_display = get_workflow_display(
                        base_display_class=display_context.workflow_display_class,
                        workflow_class=subworkflow_attribute,
                        parent_display_context=display_context,
                    )
                    subworkflow_display_context = subworkflow_display.get_event_display_context()

            node_event_displays[node_id] = NodeEventDisplayContext(
                input_display=input_display,
                output_display=output_display,
                port_display=port_display_meta,
                subworkflow_display=subworkflow_display_context,
            )

        display_meta = WorkflowEventDisplayContext(
            workflow_outputs=workflow_outputs,
            workflow_inputs=workflow_inputs,
            node_displays=node_event_displays,
        )
        return display_meta

    def _enrich_node_displays(
        self,
        node: Type[BaseNode],
        node_displays: NodeDisplays,
        global_node_displays: NodeDisplays,
        global_node_output_displays: NodeOutputDisplays,
        port_displays: PortDisplays,
    ) -> None:
        extracted_node_displays = self._extract_node_displays(node)

        for extracted_node, extracted_node_display in extracted_node_displays.items():
            if extracted_node not in node_displays:
                node_displays[extracted_node] = extracted_node_display

            if extracted_node not in global_node_displays:
                global_node_displays[extracted_node] = extracted_node_display

        self._enrich_global_node_output_displays(node, extracted_node_displays[node], global_node_output_displays)
        self._enrich_node_port_displays(node, extracted_node_displays[node], port_displays)

    def _extract_node_displays(self, node: Type[BaseNode]) -> Dict[Type[BaseNode], BaseNodeDisplay]:
        node_display = self._get_node_display(node)
        additional_node_displays: Dict[Type[BaseNode], BaseNodeDisplay] = {
            node: node_display,
        }

        # Nodes wrapped in a decorator need to be in our node display dictionary for later retrieval
        inner_node = get_wrapped_node(node)
        if inner_node:
            inner_node_displays = self._extract_node_displays(inner_node)

            for node, display in inner_node_displays.items():
                if node not in additional_node_displays:
                    additional_node_displays[node] = display

        return additional_node_displays

    def _generate_edge_display(self, edge: Edge, node_displays: Dict[Type[BaseNode], BaseNodeDisplay]) -> EdgeDisplay:
        source_node = get_unadorned_node(edge.from_port.node_class)
        target_node = get_unadorned_node(edge.to_node)

        source_node_id = node_displays[source_node].node_id
        target_node_id = node_displays[target_node].node_id

        return self._generate_edge_display_from_source(source_node_id, target_node_id)

    def _generate_edge_display_from_source(
        self,
        source_node_id: UUID,
        target_node_id: UUID,
    ) -> EdgeDisplay:
        return EdgeDisplay(
            id=uuid4_from_hash(f"{self.workflow_id}|id|{source_node_id}|{target_node_id}"),
        )

    @classmethod
    def infer_workflow_class(cls) -> Type[BaseWorkflow]:
        original_base = get_original_base(cls)
        workflow_class = get_args(original_base)[0]
        if isinstance(workflow_class, TypeVar):
            bounded_class = workflow_class.__bound__
            if inspect.isclass(bounded_class) and issubclass(bounded_class, BaseWorkflow):
                return bounded_class

            if isinstance(bounded_class, ForwardRef) and bounded_class.__forward_arg__ == BaseWorkflow.__name__:
                return BaseWorkflow

        if issubclass(workflow_class, BaseWorkflow):
            return workflow_class

        raise ValueError(f"Workflow {cls.__name__} must be a subclass of {BaseWorkflow.__name__}")

    @property
    def _workflow(self) -> Type[WorkflowType]:
        return cast(Type[WorkflowType], self.__class__.infer_workflow_class())

    @staticmethod
    def serialize_module(
        module: str,
        *,
        client: Optional[VellumClient] = None,
        dry_run: bool = False,
    ) -> WorkflowSerializationResult:
        """
        Load a workflow from a module and serialize it to JSON.

        Args:
            module: The module path to load the workflow from
            client: Optional Vellum client to use for serialization
            dry_run: Whether to run in dry-run mode

        Returns:
            WorkflowSerializationResult containing exec_config and errors
        """
        workflow = BaseWorkflow.load_from_module(module)
        workflow_display = get_workflow_display(
            workflow_class=workflow,
            client=client,
            dry_run=dry_run,
        )

        exec_config = workflow_display.serialize()
        additional_files = workflow_display._gather_additional_module_files(module)

        if additional_files:
            exec_config["module_data"] = {"additional_files": cast(JsonObject, additional_files)}

        dataset = None
        try:
            sandbox_module_path = f"{module}.sandbox"
            sandbox_module = importlib.import_module(sandbox_module_path)
            if hasattr(sandbox_module, "dataset"):
                dataset_attr = getattr(sandbox_module, "dataset")
                if dataset_attr and isinstance(dataset_attr, list):
                    dataset = []
                    for i, inputs_obj in enumerate(dataset_attr):
                        if isinstance(inputs_obj, BaseInputs):
                            serialized_inputs = json.loads(json.dumps(inputs_obj, cls=DefaultStateEncoder))
                            dataset.append({"label": f"Scenario {i + 1}", "inputs": serialized_inputs})
        except (ImportError, AttributeError):
            pass

        return WorkflowSerializationResult(
            exec_config=exec_config,
            errors=[str(error) for error in workflow_display.display_context.errors],
            dataset=dataset,
        )

    def _gather_additional_module_files(self, module_path: str) -> Dict[str, str]:
        workflow_module_path = f"{module_path}.workflow"
        workflow_module = importlib.import_module(workflow_module_path)

        workflow_file_path = workflow_module.__file__
        if not workflow_file_path:
            return {}

        module_dir = os.path.dirname(workflow_file_path)
        additional_files = {}

        for root, _, filenames in os.walk(module_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, start=module_dir)

                should_ignore = False
                for ignore_pattern in IGNORE_PATTERNS:
                    if fnmatch.fnmatch(filename, ignore_pattern) or fnmatch.fnmatch(relative_path, ignore_pattern):
                        should_ignore = True
                        break

                if not should_ignore:
                    for serialized_pattern in self._serialized_files:
                        if "*" in serialized_pattern:
                            if fnmatch.fnmatch(relative_path, serialized_pattern) or fnmatch.fnmatch(
                                filename, serialized_pattern
                            ):
                                should_ignore = True
                                break
                        else:
                            if relative_path == serialized_pattern:
                                should_ignore = True
                                break

                if should_ignore:
                    continue

                try:
                    with open(file_path, encoding="utf-8") as f:
                        additional_files[relative_path] = f.read()
                except (UnicodeDecodeError, PermissionError):
                    continue

        return additional_files

    @staticmethod
    def _is_reference_required(reference: BaseDescriptor) -> bool:
        has_default = reference.instance is not undefined
        is_optional = type(None) in reference.types
        is_required = not has_default and not is_optional
        return is_required

    def _is_node_invalid(self, node: Type[BaseNode]) -> bool:
        """Check if a node failed to serialize and should be considered invalid."""
        return node in self.display_context.invalid_nodes


register_workflow_display_class(workflow_class=BaseWorkflow, workflow_display_class=BaseWorkflowDisplay)
