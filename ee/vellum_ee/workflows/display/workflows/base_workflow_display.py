from copy import copy
from enum import Enum
import fnmatch
from functools import cached_property
import importlib
import inspect
import logging
import os
import pkgutil
import re
import sys
import traceback
from uuid import UUID
from typing import (
    Any,
    Dict,
    ForwardRef,
    FrozenSet,
    Generic,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
)

import jsonschema
from pydantic import ValidationError

from vellum.client import Vellum as VellumClient
from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.edges import Edge
from vellum.workflows.edges.trigger_edge import TriggerEdge
from vellum.workflows.events.workflow import NodeEventDisplayContext, WorkflowEventDisplayContext
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.loaders.base import BaseWorkflowFinder
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.nodes.utils import get_unadorned_node, get_unadorned_port, get_wrapped_node
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, StateValueReference, WorkflowInputReference
from vellum.workflows.sandbox import enter_serialization_context, exit_serialization_context
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.triggers.chat_message import ChatMessageTrigger
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.types.core import Json, JsonArray, JsonObject
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.uuids import generate_entity_id_from_path, uuid4_from_hash
from vellum.workflows.vellum_client import create_vellum_client
from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    StateValueDisplay,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
    WorkflowTriggerType,
    get_trigger_type_mapping,
)
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
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
from vellum_ee.workflows.display.utils.dependencies import MLModel
from vellum_ee.workflows.display.utils.exceptions import (
    StateValidationError,
    TriggerValidationError,
    UserFacingException,
    WorkflowValidationError,
)
from vellum_ee.workflows.display.utils.expressions import serialize_value
from vellum_ee.workflows.display.utils.metadata import (
    get_entrypoint_edge_id,
    get_regular_edge_id,
    get_trigger_edge_id,
    load_dataset_row_index_to_id_mapping,
    load_runner_config,
)
from vellum_ee.workflows.display.utils.registry import register_workflow_display_class
from vellum_ee.workflows.display.utils.triggers import (
    get_trigger_type,
    serialize_trigger_attributes,
    serialize_trigger_display_data,
)
from vellum_ee.workflows.display.utils.vellum import compile_descriptor_annotation, infer_vellum_variable_type
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

logger = logging.getLogger(__name__)

IGNORE_PATTERNS = [
    "*.pyc",
    "__pycache__",
    ".*",
    "node_modules/*",
    "*.log",
    "metadata.json",
]


class WorkflowSerializationError(UniversalBaseModel):
    message: str
    stacktrace: str


class WorkflowSerializationResult(UniversalBaseModel):
    exec_config: Dict[str, Any]
    errors: List[WorkflowSerializationError]
    dataset: Optional[List[Dict[str, Any]]] = None


BASE_MODULE_PATH = __name__


class _BaseWorkflowDisplayMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Type[Any], ...], attrs: Dict[str, Any]) -> Type[Any]:
        cls = super().__new__(mcs, name, bases, attrs)

        # Automatically import all of the node displays now that we don't require the __init__.py file
        # to do so for us.
        module_path = cls.__module__
        if module_path.startswith(BASE_MODULE_PATH):
            return cls

        nodes_module_path = re.sub(r"\.workflow$", ".nodes", module_path)
        try:
            nodes_module = importlib.import_module(nodes_module_path)
        except Exception:
            # likely because there are no `.nodes` module in the display workflow's module path
            return cls

        if not hasattr(nodes_module, "__path__") or not hasattr(nodes_module, "__name__"):
            return cls

        for info in pkgutil.iter_modules(nodes_module.__path__, nodes_module.__name__ + "."):
            try:
                importlib.import_module(info.name)
            except Exception:
                continue

        return cls


class BaseWorkflowDisplay(Generic[WorkflowType], metaclass=_BaseWorkflowDisplayMeta):
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
        ml_models: Optional[list] = None,
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
        self._ml_models = self._parse_ml_models(ml_models) if ml_models else []

    def _parse_ml_models(self, ml_models_raw: list) -> List[MLModel]:
        """Parse raw list of dicts into MLModel instances using pydantic deserialization.

        Models that fail validation are skipped and a warning is logged.
        """
        parsed_models: List[MLModel] = []
        for item in ml_models_raw:
            try:
                parsed_models.append(MLModel.model_validate(item))
            except Exception as e:
                model_name = item.get("name") if isinstance(item, dict) else None
                logger.warning(f"Skipping ML model '{model_name}' due to validation error: {type(e).__name__}")
        return parsed_models

    def serialize(self) -> JsonObject:
        try:
            self._workflow.validate()
        except WorkflowInitializationException as e:
            self.display_context.add_error(
                WorkflowValidationError(message=e.message, workflow_class_name=self._workflow.__name__)
            )

        self._serialized_files = [
            "__init__.py",
            "display/*",
            "inputs.py",
            "nodes/*",
            "state.py",
            "workflow.py",
            "triggers/*",
        ]

        input_variables: JsonArray = []
        for workflow_input_reference, workflow_input_display in self.display_context.workflow_input_displays.items():
            default = (
                primitive_to_vellum_value(workflow_input_reference.instance)
                if workflow_input_reference.instance is not None and workflow_input_reference.instance is not undefined
                else None
            )

            is_required = self._is_reference_required(workflow_input_reference)

            schema = compile_descriptor_annotation(workflow_input_reference)

            input_variables.append(
                {
                    "id": str(workflow_input_display.id),
                    "key": workflow_input_display.name or workflow_input_reference.name,
                    "type": infer_vellum_variable_type(workflow_input_reference),
                    "default": default.dict() if default else None,
                    "required": is_required,
                    "extensions": {"color": workflow_input_display.color},
                    "schema": schema,
                }
            )

        state_variables: JsonArray = []
        for state_value_reference, state_value_display in self.display_context.state_value_displays.items():
            default = (
                primitive_to_vellum_value(state_value_reference.instance)
                if state_value_reference.instance is not None and state_value_reference.instance is not undefined
                else None
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

        # Detect duplicate graph paths in the top-level set
        # Signature includes: regular edges (with port identity) + trigger edges
        seen_graph_signatures: Set[FrozenSet[Tuple[Literal["regular", "trigger"], int, Type[BaseNode]]]] = set()
        seen_trigger_edges: Set[Tuple[Type[BaseTrigger], Type[BaseNode]]] = set()
        trigger_edges: List[TriggerEdge] = []
        for subgraph in self._workflow.get_subgraphs():
            # Build signature from regular edges (include port identity to distinguish different ports)
            edge_signature: Set[Tuple[Any, ...]] = set()
            for edge in subgraph.edges:
                # Use port identity (id(port)) to distinguish different ports from the same node
                edge_signature.add(("regular", id(edge.from_port), get_unadorned_node(edge.to_node)))

            # Include trigger edges in the signature
            for trigger_edge in subgraph.trigger_edges:
                edge_signature.add(
                    ("trigger", id(trigger_edge.trigger_class), get_unadorned_node(trigger_edge.to_node))
                )

            frozen_signature = frozenset(edge_signature)
            if frozen_signature and frozen_signature in seen_graph_signatures:
                self.display_context.add_validation_error(
                    WorkflowValidationError(
                        message="Duplicate graph path detected in workflow",
                        workflow_class_name=self._workflow.__name__,
                    )
                )
            elif frozen_signature:
                seen_graph_signatures.add(frozen_signature)

            # Collect and deduplicate trigger edges (for the trigger_edges list only)
            for trigger_edge in subgraph.trigger_edges:
                edge_key = (trigger_edge.trigger_class, get_unadorned_node(trigger_edge.to_node))
                if edge_key not in seen_trigger_edges:
                    seen_trigger_edges.add(edge_key)
                    trigger_edges.append(trigger_edge)

        # Determine if we need an ENTRYPOINT node and what ID to use
        manual_trigger_edges = [edge for edge in trigger_edges if issubclass(edge.trigger_class, ManualTrigger)]
        has_manual_trigger = len(manual_trigger_edges) > 0

        # Determine which nodes have explicit non-trigger entrypoints in the graph
        # This is used to decide whether to create an ENTRYPOINT node and skip entrypoint edges
        non_trigger_entrypoint_nodes: Set[Type[BaseNode]] = set()
        for subgraph in self._workflow.get_subgraphs():
            if any(True for _ in subgraph.trigger_edges):
                continue
            for entrypoint in subgraph.entrypoints:
                try:
                    non_trigger_entrypoint_nodes.add(get_unadorned_node(entrypoint))
                except Exception:
                    continue

        # Determine if we need an ENTRYPOINT node:
        # - ManualTrigger: always need ENTRYPOINT (backward compatibility)
        # - No triggers: always need ENTRYPOINT (traditional workflows)
        # - Non-trigger entrypoints exist: need ENTRYPOINT for those branches
        # - Only non-manual triggers with no regular entrypoints: skip ENTRYPOINT
        has_triggers = len(trigger_edges) > 0
        needs_entrypoint_node = has_manual_trigger or not has_triggers or len(non_trigger_entrypoint_nodes) > 0

        # Validate that the workflow has at least one trigger or entrypoint node
        if not has_triggers and len(non_trigger_entrypoint_nodes) == 0:
            self.display_context.add_validation_error(
                WorkflowValidationError(
                    message="Workflow has no triggers and no entrypoint nodes. "
                    "A workflow must have at least one trigger or one node in its graph.",
                    workflow_class_name=self._workflow.__name__,
                )
            )

        entrypoint_node_id: Optional[UUID] = None
        entrypoint_node_source_handle_id: Optional[UUID] = None
        entrypoint_node_display = self.display_context.workflow_display.entrypoint_node_display

        if has_manual_trigger:
            # ManualTrigger: use trigger ID for ENTRYPOINT node (backward compatibility)
            trigger_class = manual_trigger_edges[0].trigger_class
            entrypoint_node_id = trigger_class.__id__
            entrypoint_node_source_handle_id = self.display_context.workflow_display.entrypoint_node_source_handle_id

            # Add ENTRYPOINT node for ManualTrigger workflows
            serialized_nodes[entrypoint_node_id] = {
                "id": str(entrypoint_node_id),
                "type": "ENTRYPOINT",
                "inputs": [],
                "data": {
                    "label": "Entrypoint Node",
                    "source_handle_id": str(entrypoint_node_source_handle_id),
                },
                "display_data": entrypoint_node_display.dict() if entrypoint_node_display else NodeDisplayData().dict(),
                "base": None,
                "definition": None,
            }
        elif needs_entrypoint_node:
            # No triggers or non-trigger entrypoints exist: use workflow_display ENTRYPOINT node
            entrypoint_node_id = self.display_context.workflow_display.entrypoint_node_id
            entrypoint_node_source_handle_id = self.display_context.workflow_display.entrypoint_node_source_handle_id

            if entrypoint_node_id is not None and entrypoint_node_source_handle_id is not None:
                display_data = entrypoint_node_display.dict() if entrypoint_node_display else NodeDisplayData().dict()
                serialized_nodes[entrypoint_node_id] = {
                    "id": str(entrypoint_node_id),
                    "type": "ENTRYPOINT",
                    "inputs": [],
                    "data": {
                        "label": "Entrypoint Node",
                        "source_handle_id": str(entrypoint_node_source_handle_id),
                    },
                    "display_data": display_data,
                    "base": None,
                    "definition": None,
                }
        # else: only non-manual triggers with no regular entrypoints - skip ENTRYPOINT node

        # Add all the nodes in the workflows
        for node in self._workflow.get_all_nodes():
            node_display = self.display_context.node_displays[node]

            try:
                try:
                    node.__validate__()
                except (ValueError, jsonschema.exceptions.SchemaError) as validation_error:
                    # Only collect node validation errors directly to errors list, don't raise them
                    self.display_context.add_validation_error(validation_error)

                serialized_node = node_display.serialize(self.display_context)
            except (NotImplementedError, UserFacingException) as e:
                self.display_context.add_error(e)
                self.display_context.add_invalid_node(node)
                continue

            # Use wrapped node's ID as dict key for adornment wrappers to prevent overwrites
            wrapped_node = get_wrapped_node(node)
            if wrapped_node:
                wrapped_node_display = self.display_context.node_displays[wrapped_node]
                dict_key = wrapped_node_display.node_id
            else:
                dict_key = node_display.node_id

            serialized_nodes[dict_key] = serialized_node

        output_variables: JsonArray = []
        output_values: JsonArray = []
        final_output_nodes = [
            node for node in self.display_context.node_displays.keys() if issubclass(node, FinalOutputNode)
        ]
        final_output_node_outputs = {node.Outputs.value for node in final_output_nodes}
        unreferenced_final_output_node_outputs = final_output_node_outputs.copy()

        # Track the Workflow's output variables for each Workflow output
        for workflow_output, workflow_output_display in self.display_context.workflow_output_displays.items():
            inferred_type = infer_vellum_variable_type(workflow_output)
            # Remove the terminal node output from the unreferenced set
            if isinstance(workflow_output.instance, OutputReference):
                unreferenced_final_output_node_outputs.discard(workflow_output.instance)

            # Update the name of the terminal node if this output references a FinalOutputNode
            if workflow_output.instance in final_output_node_outputs:
                terminal_node_id = workflow_output.instance.outputs_class.__parent_class__.__id__
                serialized_terminal_node = serialized_nodes.get(terminal_node_id)
                if (
                    serialized_terminal_node
                    and "data" in serialized_terminal_node
                    and isinstance(serialized_terminal_node["data"], dict)
                ):
                    serialized_terminal_node["data"]["name"] = workflow_output_display.name

            try:
                output_value = self.serialize_value(workflow_output.instance)
            except UserFacingException as e:
                self.display_context.add_error(
                    UserFacingException(f"Failed to serialize output '{workflow_output.name}': {e}")
                )
                continue

            output_values.append(
                {
                    "output_variable_id": str(workflow_output_display.id),
                    "value": output_value,
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
                WorkflowValidationError(
                    message="Unable to serialize terminal nodes that are not referenced by workflow outputs.",
                    workflow_class_name=self._workflow.__name__,
                )
            )

        # Identify nodes that already have trigger edges so we can avoid duplicating entrypoint edges
        nodes_with_manual_trigger_edges: Set[Type[BaseNode]] = set()
        nodes_with_non_manual_trigger_edges: Set[Type[BaseNode]] = set()
        for trigger_edge in trigger_edges:
            try:
                unadorned_target_node = get_unadorned_node(trigger_edge.to_node)
            except Exception:
                continue

            if issubclass(trigger_edge.trigger_class, ManualTrigger):
                nodes_with_manual_trigger_edges.add(unadorned_target_node)
            else:
                nodes_with_non_manual_trigger_edges.add(unadorned_target_node)

        # Track nodes with explicit entrypoint overrides so we retain their edges even if they have triggers
        entrypoint_override_nodes: Set[Type[BaseNode]] = set()
        for entrypoint_node in self.entrypoint_displays.keys():
            try:
                entrypoint_override_nodes.add(get_unadorned_node(entrypoint_node))
            except Exception:
                continue

        # Add edges from entrypoint first to preserve expected ordering
        # Note: non_trigger_entrypoint_nodes was computed earlier to determine if we need an ENTRYPOINT node

        for target_node, entrypoint_display in self.display_context.entrypoint_displays.items():
            unadorned_target_node = get_unadorned_node(target_node)

            # Skip the auto-generated entrypoint edge when a manual trigger already targets this node or when a
            # non-manual trigger targets it without an explicit entrypoint override, unless the graph explicitly
            # defines a non-trigger entrypoint for it.
            has_manual_trigger = unadorned_target_node in nodes_with_manual_trigger_edges
            has_non_manual_trigger = unadorned_target_node in nodes_with_non_manual_trigger_edges
            has_override = unadorned_target_node in entrypoint_override_nodes
            if (
                has_manual_trigger or (has_non_manual_trigger and not has_override)
            ) and unadorned_target_node not in non_trigger_entrypoint_nodes:
                continue

            # Skip edges to invalid nodes
            if self._is_node_invalid(unadorned_target_node):
                continue

            if entrypoint_node_id is None:
                continue

            target_node_display = self.display_context.node_displays[unadorned_target_node]

            stable_edge_id = get_entrypoint_edge_id(unadorned_target_node, self._workflow.__module__)

            entrypoint_edge_dict: Dict[str, Json] = {
                "id": str(stable_edge_id) if stable_edge_id else str(entrypoint_display.edge_display.id),
                "source_node_id": str(entrypoint_node_id),
                "source_handle_id": str(entrypoint_node_source_handle_id),
                "target_node_id": str(target_node_display.node_id),
                "target_handle_id": str(target_node_display.get_trigger_id()),
                "type": "DEFAULT",
            }
            edge_display_data = self._serialize_edge_display_data(entrypoint_display.edge_display)
            if edge_display_data is not None:
                entrypoint_edge_dict["display_data"] = edge_display_data
            edges.append(entrypoint_edge_dict)

        # Then add trigger edges
        for trigger_edge in trigger_edges:
            target_node = trigger_edge.to_node
            unadorned_target_node = get_unadorned_node(target_node)
            if issubclass(trigger_edge.trigger_class, ManualTrigger):
                nodes_with_manual_trigger_edges.add(unadorned_target_node)
            else:
                nodes_with_non_manual_trigger_edges.add(unadorned_target_node)

            # Skip edges to invalid nodes
            if self._is_node_invalid(unadorned_target_node):
                continue

            target_node_display = self.display_context.node_displays[unadorned_target_node]

            # Get the entrypoint display for this target node (if it exists)
            target_entrypoint_display = self.display_context.entrypoint_displays.get(target_node)
            if target_entrypoint_display is None:
                continue

            trigger_class = trigger_edge.trigger_class
            trigger_id = trigger_class.__id__

            # Determine source node ID and handle ID based on trigger type
            if issubclass(trigger_class, ManualTrigger):
                source_node_id = entrypoint_node_id
                source_handle_id = entrypoint_node_source_handle_id
            else:
                source_node_id = trigger_id
                source_handle_id = trigger_id

            # Prefer stable id from metadata mapping if present
            stable_edge_id = get_trigger_edge_id(trigger_class, unadorned_target_node, self._workflow.__module__)

            # Generate a unique fallback edge ID using trigger_id and target_node_id
            # This ensures multiple triggers targeting the same node get unique edge IDs
            fallback_edge_id = uuid4_from_hash(
                f"{self.workflow_id}|trigger_edge|{trigger_id}|{target_node_display.node_id}"
            )

            trigger_edge_dict: Dict[str, Json] = {
                "id": str(stable_edge_id) if stable_edge_id else str(fallback_edge_id),
                "source_node_id": str(source_node_id),
                "source_handle_id": str(source_handle_id),
                "target_node_id": str(target_node_display.node_id),
                "target_handle_id": str(target_node_display.get_trigger_id()),
                "type": "DEFAULT",
            }
            trigger_edge_display_data = self._serialize_edge_display_data(target_entrypoint_display.edge_display)
            if trigger_edge_display_data is not None:
                trigger_edge_dict["display_data"] = trigger_edge_display_data
            edges.append(trigger_edge_dict)

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

            stable_edge_id = get_regular_edge_id(
                unadorned_source_node_port.node_class,
                source_node_port_display.id,
                unadorned_target_node,
                self._workflow.__module__,
            )

            regular_edge_dict: Dict[str, Json] = {
                "id": str(stable_edge_id) if stable_edge_id else str(edge_display.id),
                "source_node_id": str(source_node_port_display.node_id),
                "source_handle_id": str(source_node_port_display.id),
                "target_node_id": str(target_node_display.node_id),
                "target_handle_id": str(
                    target_node_display.get_target_handle_id_by_source_node_id(source_node_port_display.node_id)
                ),
                "type": "DEFAULT",
            }
            regular_edge_display_data = self._serialize_edge_display_data(edge_display)
            if regular_edge_display_data is not None:
                regular_edge_dict["display_data"] = regular_edge_display_data
            edges.append(regular_edge_dict)

        nodes_list = list(serialized_nodes.values())
        nodes_dict_list = [cast(Dict[str, Any], node) for node in nodes_list if isinstance(node, dict)]

        workflow_layout = getattr(self._workflow.Display, "layout", None)
        should_apply_auto_layout = workflow_layout == "auto" and len(nodes_dict_list) > 0

        if should_apply_auto_layout:
            try:
                self._apply_auto_layout(nodes_dict_list, edges)
            except Exception as e:
                self.display_context.add_error(e)

        # Serialize workflow-level trigger if present
        triggers: Optional[JsonArray] = self._serialize_workflow_trigger()

        workflow_raw_data: JsonObject = {
            "nodes": cast(JsonArray, nodes_dict_list),
            "edges": edges,
            "display_data": self.display_context.workflow_display.display_data.dict(),
            "definition": {
                "name": self._workflow.__name__,
                "module": cast(JsonArray, self._workflow.__module__.split(".")),
            },
            "output_values": output_values,
        }

        result: JsonObject = {
            "workflow_raw_data": workflow_raw_data,
            "input_variables": input_variables,
            "state_variables": state_variables,
            "output_variables": output_variables,
        }

        if triggers is not None:
            result["triggers"] = triggers

        # Get dependencies that were registered during node serialization
        dependencies = self.display_context.get_dependencies()
        if dependencies:
            result["dependencies"] = cast(JsonArray, dependencies)

        return result

    def _serialize_workflow_trigger(self) -> Optional[JsonArray]:
        """
        Serialize workflow-level trigger information.

        Returns:
            JsonArray with trigger data if a trigger is present, None otherwise.
            Each trigger in the array has: id (UUID), type (str), name (str), attributes (list)
        """
        # Get all trigger edges from the workflow's subgraphs
        trigger_edges = []
        for subgraph in self._workflow.get_subgraphs():
            trigger_edges.extend(list(subgraph.trigger_edges))

        if not trigger_edges:
            # No workflow-level trigger defined
            return None

        unique_trigger_classes = list(dict.fromkeys(edge.trigger_class for edge in trigger_edges))

        trigger_type_mapping = get_trigger_type_mapping()
        serialized_triggers: List[JsonObject] = []
        seen_trigger_names: Set[str] = set()

        for trigger_class in unique_trigger_classes:
            # Get the trigger type from the mapping, or use the utility function
            trigger_type = trigger_type_mapping.get(trigger_class)
            if trigger_type is None:
                trigger_type = get_trigger_type(trigger_class)

            trigger_id = trigger_class.__id__

            # Determine trigger name from the trigger class's __trigger_name__ attribute
            trigger_name = trigger_class.__trigger_name__

            # Validate that trigger names are unique
            if trigger_name in seen_trigger_names:
                self.display_context.add_validation_error(
                    TriggerValidationError(
                        message=f"Duplicate trigger name '{trigger_name}' found. Each trigger must have a unique name.",
                        trigger_class_name=trigger_class.__name__,
                    )
                )
            seen_trigger_names.add(trigger_name)

            # Serialize trigger attributes using the shared utility
            trigger_attributes = serialize_trigger_attributes(trigger_class)

            trigger_data: JsonObject
            if trigger_type == WorkflowTriggerType.SCHEDULED:
                # For scheduled triggers, include cron/timezone at top level
                config_class = trigger_class.Config
                cron_value = getattr(config_class, "cron", None)
                timezone_value = getattr(config_class, "timezone", None)

                trigger_data = {
                    "id": str(trigger_id),
                    "type": trigger_type.value,
                    "name": trigger_name,
                    "cron": cron_value,
                    "timezone": timezone_value,
                    "attributes": trigger_attributes,
                }
            else:
                # For other triggers (integration, etc.)
                trigger_data = {
                    "id": str(trigger_id),
                    "type": trigger_type.value,
                    "name": trigger_name,
                    "attributes": trigger_attributes,
                }

                if trigger_type == WorkflowTriggerType.INTEGRATION and issubclass(trigger_class, IntegrationTrigger):
                    exec_config = self._serialize_integration_trigger_exec_config(trigger_class)
                    trigger_data["exec_config"] = exec_config

                    # Validate trigger attributes against the expected types from the API
                    self._validate_integration_trigger_attributes(trigger_class, trigger_attributes)

                if trigger_type == WorkflowTriggerType.CHAT_MESSAGE and issubclass(trigger_class, ChatMessageTrigger):
                    chat_exec_config = self._serialize_chat_message_trigger_exec_config(trigger_class)
                    if chat_exec_config:
                        trigger_data["exec_config"] = chat_exec_config

            # Serialize display_data using the shared utility
            display_data = serialize_trigger_display_data(trigger_class, trigger_type)

            # Don't include display_data for manual triggers
            if display_data and trigger_type != WorkflowTriggerType.MANUAL:
                trigger_data["display_data"] = display_data

            serialized_triggers.append(trigger_data)

        return cast(JsonArray, serialized_triggers)

    def _serialize_edge_display_data(self, edge_display: EdgeDisplay) -> Optional[JsonObject]:
        """Serialize edge display data, returning None if no display data is present."""
        if edge_display.z_index is not None:
            return {"z_index": edge_display.z_index}
        return None

    def _serialize_integration_trigger_exec_config(self, trigger_class: Type[IntegrationTrigger]) -> JsonObject:
        config_class = trigger_class.Config

        provider = getattr(config_class, "provider", None)
        if isinstance(provider, Enum):
            provider = provider.value
        elif provider is not None:
            provider = str(provider)
        slug = getattr(config_class, "slug", None)
        integration_name = getattr(config_class, "integration_name", None)

        setup_attributes: List[JsonObject] = []
        raw_setup_attributes = getattr(config_class, "setup_attributes", None)

        if isinstance(raw_setup_attributes, dict):
            for key, value in raw_setup_attributes.items():
                attribute_id = str(uuid4_from_hash(f"{trigger_class.__id__}|setup_attribute|{key}"))

                default_json: Optional[JsonObject] = None
                attribute_type = "STRING"

                if value is not None:
                    try:
                        vellum_value = primitive_to_vellum_value(value)
                        default_json = cast(JsonObject, self._model_dump(vellum_value))
                        attribute_type = cast(str, default_json.get("type", attribute_type))
                    except ValueError:
                        default_json = None

                setup_attributes.append(
                    cast(
                        JsonObject,
                        {
                            "id": attribute_id,
                            "key": str(key),
                            "type": attribute_type,
                            "required": True,
                            "default": default_json,
                            "extensions": {"color": None, "description": None},
                        },
                    )
                )

        return cast(
            JsonObject,
            {
                "type": provider,
                "slug": slug,
                "integration_name": integration_name,
                "setup_attributes": setup_attributes,
            },
        )

    def _fetch_integration_trigger_definition(
        self, provider: str, integration_name: str, trigger_slug: str
    ) -> Optional[JsonObject]:
        """
        Fetch the trigger/tool definition from the API to get the expected attribute types.

        Uses the client's integrations.retrieve_integration_tool_definition method.

        Returns the tool definition with output_parameters (payload schema) if found, None otherwise.
        For triggers, output_parameters contains the webhook payload schema, while input_parameters
        contains setup/config arguments.
        """
        try:
            tool_definition = self._client.integrations.retrieve_integration_tool_definition(
                integration_name=integration_name,
                integration_provider=provider,
                tool_name=trigger_slug,
            )
            return cast(
                JsonObject,
                {
                    "name": tool_definition.name,
                    "output_parameters": tool_definition.output_parameters,
                },
            )
        except Exception as e:
            logger.warning(f"Error fetching tool definition for {trigger_slug}: {e}")
            return None

    def _validate_integration_trigger_attributes(
        self,
        trigger_class: Type[IntegrationTrigger],
        trigger_attributes: JsonArray,
    ) -> None:
        """
        Validate that the trigger attributes match the expected types from the API.

        Raises TriggerValidationError if there's a type mismatch.
        """
        config_class = trigger_class.Config
        provider = getattr(config_class, "provider", None)
        if isinstance(provider, Enum):
            provider = provider.value
        elif provider is not None:
            provider = str(provider)

        slug = getattr(config_class, "slug", None)
        integration_name = getattr(config_class, "integration_name", None)

        if not provider or not slug or not integration_name:
            return

        trigger_def = self._fetch_integration_trigger_definition(provider, integration_name, slug)
        if not trigger_def:
            return

        # output_parameters contains the webhook payload schema for triggers
        # (input_parameters contains setup/config arguments like team_id)
        output_parameters = trigger_def.get("output_parameters", {})
        if not output_parameters or not isinstance(output_parameters, dict):
            return

        # output_parameters is a JSON Schema object with structure:
        # {"type": "object", "properties": {"key": {"type": "string"}, ...}, "required": [...]}
        properties = output_parameters.get("properties", {})
        if not properties or not isinstance(properties, dict):
            return

        # Map JSON Schema types to Vellum attribute types
        json_schema_to_vellum_type: Dict[str, str] = {
            "string": "STRING",
            "number": "NUMBER",
            "integer": "NUMBER",
            "boolean": "BOOLEAN",
            "object": "JSON",
            "array": "ARRAY",
        }

        expected_types_by_key: Dict[str, str] = {}
        for key, param_info in properties.items():
            if not isinstance(param_info, dict):
                continue
            param_type = param_info.get("type")
            if isinstance(param_type, str):
                vellum_type = json_schema_to_vellum_type.get(param_type)
                if vellum_type:
                    expected_types_by_key[key] = vellum_type

        for attr in trigger_attributes:
            if not isinstance(attr, dict):
                continue
            attr_key = attr.get("key")
            actual_type = attr.get("type")
            if isinstance(attr_key, str) and isinstance(actual_type, str) and attr_key in expected_types_by_key:
                expected_type = expected_types_by_key[attr_key]
                if actual_type != expected_type:
                    raise TriggerValidationError(
                        message=f"Attribute '{attr_key}' has type '{actual_type}' but expected type '{expected_type}'. "
                        "The trigger configuration is invalid or contains unsupported values.",
                        trigger_class_name=trigger_class.__name__,
                    )

    def _serialize_chat_message_trigger_exec_config(
        self, trigger_class: Type[ChatMessageTrigger]
    ) -> Optional[JsonObject]:
        config_class = trigger_class.Config
        output = getattr(config_class, "output", None)

        if output is None:
            self.display_context.add_validation_error(
                TriggerValidationError(
                    message="Chat Trigger output must be specified.",
                    trigger_class_name=trigger_class.__name__,
                )
            )
            return None

        self._validate_chat_history_state(trigger_class)

        serialized_output = serialize_value(
            executable_id=trigger_class.__id__,
            display_context=self.display_context,
            value=output,
        )

        return cast(
            JsonObject,
            {
                "output": serialized_output,
            },
        )

    def _validate_chat_history_state(self, trigger_class: Type[ChatMessageTrigger]) -> None:
        state_class = self._workflow.get_state_class()

        if not hasattr(state_class, "chat_history"):
            self.display_context.add_validation_error(
                StateValidationError(
                    message=(
                        "Chat triggers require a `chat_history` state variable. "
                        "Add `chat_history: List[ChatMessage] = Field(default_factory=list)` to your state class."
                    ),
                    state_class_name=state_class.__name__,
                    attribute_name="chat_history",
                )
            )
            return

        chat_history_ref = getattr(state_class, "chat_history")
        if chat_history_ref.instance is None:
            self.display_context.add_validation_error(
                StateValidationError(
                    message=(
                        "Chat triggers expect chat_history to default to an empty array. "
                        "Use `Field(default_factory=list)` instead of `= None`."
                    ),
                    state_class_name=state_class.__name__,
                    attribute_name="chat_history",
                )
            )

    @staticmethod
    def _model_dump(value: Any) -> Any:
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        if hasattr(value, "dict"):
            return value.dict()
        return value

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
        node_output_displays: Dict[OutputReference, NodeOutputDisplay],
        node_displays: NodeDisplays,
        errors: List[Exception],
    ):
        """This method recursively adds nodes wrapped in decorators to the node_output_displays dictionary."""

        inner_node = get_wrapped_node(node)
        if inner_node:
            inner_node_display = node_displays.get(inner_node) or self._get_node_display(inner_node, errors)
            self._enrich_global_node_output_displays(
                inner_node, inner_node_display, node_output_displays, node_displays, errors
            )

        for node_output in node.Outputs:
            if node_output in node_output_displays:
                continue

            node_output_displays[node_output] = node_display.get_node_output_display(node_output)

    def _enrich_node_port_displays(
        self,
        node: Type[BaseNode],
        node_display: BaseNodeDisplay,
        port_displays: Dict[Port, PortDisplay],
        node_displays: NodeDisplays,
        errors: List[Exception],
    ):
        """This method recursively adds nodes wrapped in decorators to the port_displays dictionary."""

        inner_node = get_wrapped_node(node)
        if inner_node:
            inner_node_display = node_displays.get(inner_node) or self._get_node_display(inner_node, errors)
            self._enrich_node_port_displays(inner_node, inner_node_display, port_displays, node_displays, errors)

        for port in node.Ports:
            if port in port_displays:
                continue

            port_displays[port] = node_display.get_node_port_display(port)

    def _get_node_display(self, node: Type[BaseNode], errors: List[Exception]) -> BaseNodeDisplay:
        node_display_class = get_node_display_class(node)
        node_display = node_display_class()
        try:
            node_display.build(client=self._client)
        except Exception as e:
            errors.append(e)
        return node_display

    @cached_property
    def display_context(self) -> WorkflowDisplayContext:
        errors: List[Exception] = []
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
                errors=errors,
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
            self._validate_state_value_default(state_value, errors)
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
                workflow_output_display or self._generate_workflow_output_display(workflow_output)
            )

        # For ml_models, inherit from parent context if available (for nested workflows)
        # Otherwise use the ml_models parsed from __init__
        ml_models = self._parent_display_context.ml_models if self._parent_display_context else self._ml_models

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
            dry_run=self._dry_run,
            ml_models=ml_models,
            _errors=errors,
        )

    def _generate_workflow_meta_display(self) -> WorkflowMetaDisplay:
        defaults = WorkflowMetaDisplay.get_default(self._workflow)
        overrides = self.workflow_display

        if not overrides:
            return defaults

        # Merge overrides with defaults - if override provides None, fall back to default
        entrypoint_node_id = (
            overrides.entrypoint_node_id if overrides.entrypoint_node_id is not None else defaults.entrypoint_node_id
        )
        entrypoint_node_source_handle_id = (
            overrides.entrypoint_node_source_handle_id
            if overrides.entrypoint_node_source_handle_id is not None
            else defaults.entrypoint_node_source_handle_id
        )
        entrypoint_node_display = (
            overrides.entrypoint_node_display
            if overrides.entrypoint_node_display is not None
            else defaults.entrypoint_node_display
        )

        return WorkflowMetaDisplay(
            entrypoint_node_id=entrypoint_node_id,
            entrypoint_node_source_handle_id=entrypoint_node_source_handle_id,
            entrypoint_node_display=entrypoint_node_display,
            display_data=overrides.display_data,
        )

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
            workflow_input_id = workflow_input.id

        return WorkflowInputsDisplay(id=workflow_input_id, name=name, color=color)

    def _generate_state_value_display(
        self, state_value: StateValueReference, overrides: Optional[StateValueDisplay] = None
    ) -> StateValueDisplay:
        state_value_id: UUID
        name = None
        color = None
        if overrides:
            state_value_id = overrides.id
            name = overrides.name
            color = overrides.color
        else:
            state_value_id = state_value.id

        return StateValueDisplay(id=state_value_id, name=name, color=color)

    def _validate_state_value_default(self, state_value: StateValueReference, errors: List[Exception]) -> None:
        default_value = state_value.instance

        if isinstance(default_value, (list, dict, set)):
            errors.append(
                StateValidationError(
                    message=(
                        "Mutable default value detected. Use Field(default_factory=list) instead of = [] "
                        "to avoid shared mutable state between instances."
                    ),
                    state_class_name=state_value.state_class.__name__,
                    attribute_name=state_value.name,
                )
            )

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

        if edge_display_overrides:
            edge_display = edge_display_overrides
        elif entrypoint_node_id is not None:
            edge_display = self._generate_edge_display_from_source(entrypoint_node_id, target_node_id)
        else:
            edge_display = EdgeDisplay(id=uuid4_from_hash(f"{self.workflow_id}|id|{target_node_id}"))

        return EntrypointDisplay(id=entrypoint_id, edge_display=edge_display)

    def _generate_workflow_output_display(self, output: OutputReference) -> WorkflowOutputDisplay:
        return WorkflowOutputDisplay(id=output.id, name=output.name)

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

        # Include trigger attributes in workflow_inputs so they appear in the executions list UI
        for subgraph in self._workflow.get_subgraphs():
            for trigger_class in subgraph.triggers:
                for trigger_attr_ref in trigger_class:
                    if trigger_attr_ref.name not in workflow_inputs:
                        workflow_inputs[trigger_attr_ref.name] = trigger_attr_ref.id
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
        errors: List[Exception],
    ) -> None:
        if node in node_displays:
            return

        extracted_node_displays = self._extract_node_displays(node, errors)

        for extracted_node, extracted_node_display in extracted_node_displays.items():
            if extracted_node not in node_displays:
                node_displays[extracted_node] = extracted_node_display

            if extracted_node not in global_node_displays:
                global_node_displays[extracted_node] = extracted_node_display

        self._enrich_global_node_output_displays(
            node, extracted_node_displays[node], global_node_output_displays, node_displays, errors
        )
        self._enrich_node_port_displays(node, extracted_node_displays[node], port_displays, node_displays, errors)

    def _extract_node_displays(
        self, node: Type[BaseNode], errors: List[Exception]
    ) -> Dict[Type[BaseNode], BaseNodeDisplay]:
        node_display = self._get_node_display(node, errors)
        additional_node_displays: Dict[Type[BaseNode], BaseNodeDisplay] = {
            node: node_display,
        }

        # Nodes wrapped in a decorator need to be in our node display dictionary for later retrieval
        inner_node = get_wrapped_node(node)
        if inner_node:
            inner_node_displays = self._extract_node_displays(inner_node, errors)

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
    def _collect_node_classes_from_module(
        module: Any,
        expected_module_prefix: str,
    ) -> List[Type[BaseNode]]:
        """
        Collect BaseNode subclasses defined in a module.

        Args:
            module: The imported module to scan
            expected_module_prefix: Module path prefix to filter by (e.g., "my_module")

        Returns:
            List of BaseNode subclasses defined in the module
        """
        node_classes: List[Type[BaseNode]] = []
        for name, attr in vars(module).items():
            if name.startswith("_"):
                continue

            if not (inspect.isclass(attr) and issubclass(attr, BaseNode) and attr is not BaseNode):
                continue

            if not attr.__module__.startswith(expected_module_prefix):
                continue

            if "<locals>" in attr.__qualname__:
                continue

            node_classes.append(attr)

        return node_classes

    @staticmethod
    def _find_orphan_nodes(
        base_module: str,
        workflow: Type[BaseWorkflow],
    ) -> List[Type[BaseNode]]:
        """
        Find nodes defined in the workflow package but not included in graph or unused_graphs.

        Scans both the workflow.py file and the nodes/ subpackage for BaseNode subclasses.

        Args:
            base_module: The base module path (e.g., "my_module")
            workflow: The workflow class to check

        Returns:
            List of orphan node classes
        """
        workflow_nodes = set(workflow.get_all_nodes())
        candidate_nodes: List[Type[BaseNode]] = []

        workflow_module_path = f"{base_module}.workflow"
        try:
            workflow_module = importlib.import_module(workflow_module_path)
            candidate_nodes.extend(BaseWorkflowDisplay._collect_node_classes_from_module(workflow_module, base_module))
        except ImportError:
            pass

        nodes_package_path = f"{base_module}.nodes"
        try:
            nodes_package = importlib.import_module(nodes_package_path)
            if hasattr(nodes_package, "__path__"):
                for module_info in pkgutil.walk_packages(nodes_package.__path__, nodes_package.__name__ + "."):
                    try:
                        submodule = importlib.import_module(module_info.name)
                        candidate_nodes.extend(
                            BaseWorkflowDisplay._collect_node_classes_from_module(submodule, base_module)
                        )
                    except Exception:
                        continue
        except ImportError:
            pass

        seen: Set[Type[BaseNode]] = set()
        orphan_nodes: List[Type[BaseNode]] = []
        for node in candidate_nodes:
            if node in seen:
                continue
            seen.add(node)
            if node not in workflow_nodes:
                orphan_nodes.append(node)

        return orphan_nodes

    @staticmethod
    def serialize_module(
        module: str,
        *,
        client: Optional[VellumClient] = None,
        dry_run: bool = False,
        ml_models: Optional[list] = None,
    ) -> WorkflowSerializationResult:
        """
        Load a workflow from a module and serialize it to JSON.

        Args:
            module: The module path to load the workflow from
            client: Optional Vellum client to use for serialization
            dry_run: Whether to run in dry-run mode
            ml_models: Optional list of ML model definitions for dependency extraction

        Returns:
            WorkflowSerializationResult containing exec_config and errors
        """
        try:
            workflow = BaseWorkflow.load_from_module(module)
        except WorkflowInitializationException as e:
            # Only handle ValidationError gracefully when dry_run=True (matching production behavior)
            # Other WorkflowInitializationExceptions (e.g., invalid graph structure) should still raise
            if dry_run and isinstance(e.__cause__, ValidationError):
                return WorkflowSerializationResult(
                    exec_config={},
                    errors=[
                        WorkflowSerializationError(
                            message=str(e),
                            stacktrace="".join(traceback.format_exception(type(e), e, e.__traceback__)),
                        )
                    ],
                    dataset=None,
                )
            raise
        workflow_display = get_workflow_display(
            workflow_class=workflow,
            client=client,
            dry_run=dry_run,
            ml_models=ml_models,
        )

        orphan_nodes = BaseWorkflowDisplay._find_orphan_nodes(module, workflow)
        for orphan_node in orphan_nodes:
            workflow_display.display_context.add_validation_error(
                WorkflowValidationError(
                    message=f"Node '{orphan_node.__name__}' is defined in the module but not included in "
                    "the workflow's graph or unused_graphs.",
                    workflow_class_name=workflow.__name__,
                )
            )

        exec_config = workflow_display.serialize()
        additional_files = workflow_display._gather_additional_module_files(module)

        if additional_files:
            exec_config["module_data"] = {"additional_files": cast(JsonObject, additional_files)}

        exec_config["runner_config"] = load_runner_config(module)

        dataset = None
        serialization_errors = []
        try:
            sandbox_module_path = f"{module}.sandbox"
            context_token, errors_token = enter_serialization_context()
            try:
                sandbox_module = importlib.import_module(sandbox_module_path)
            finally:
                serialization_errors = exit_serialization_context(context_token, errors_token)
            if hasattr(sandbox_module, "dataset"):
                dataset_attr = getattr(sandbox_module, "dataset")
                if dataset_attr and isinstance(dataset_attr, list):
                    dataset = []
                    dataset_row_index_to_id = load_dataset_row_index_to_id_mapping(module)
                    for i, inputs_obj in enumerate(dataset_attr):
                        normalized_row = (
                            DatasetRow(label=f"Scenario {i + 1}", inputs=inputs_obj)
                            if isinstance(inputs_obj, BaseInputs)
                            else inputs_obj
                        )

                        row_data = normalized_row.model_dump(
                            mode="json",
                            by_alias=True,
                            exclude_none=True,
                            context={
                                "add_error": workflow_display.display_context.add_validation_error,
                                "serializer": workflow_display.serialize_value,
                            },
                        )

                        if i in dataset_row_index_to_id:
                            row_data["id"] = dataset_row_index_to_id[i]
                        elif isinstance(inputs_obj, DatasetRow) and inputs_obj.id is not None:
                            row_data["id"] = inputs_obj.id
                        else:
                            row_data["id"] = str(generate_entity_id_from_path(f"{module}.sandbox.dataset.{i}"))

                        dataset.append(row_data)
        except ImportError:
            # No sandbox module exists, which is fine
            pass
        except Exception as e:
            # Capture any other errors (AttributeError, TypeError, etc.) from sandbox module
            workflow_display.display_context.add_validation_error(e)

        all_errors = list(workflow_display.display_context.errors)

        # Build error list from display context errors
        error_list = [
            WorkflowSerializationError(
                message=str(error),
                stacktrace="".join(traceback.format_exception(type(error), error, error.__traceback__)),
            )
            for error in all_errors
        ]

        # Add serialization errors (runner.run() called during serialization)
        for error, stacktrace in serialization_errors:
            error_list.append(
                WorkflowSerializationError(
                    message=str(error),
                    stacktrace=stacktrace,
                )
            )

        return WorkflowSerializationResult(
            exec_config=exec_config,
            errors=error_list,
            dataset=dataset,
        )

    def serialize_value(self, value: Any) -> Any:
        return serialize_value(self.workflow_id, self.display_context, value)

    _INCLUDED_FILE_EXTENSIONS = [".py"]
    _INCLUDED_FILENAMES = ["metadata.json"]

    @staticmethod
    def should_include_file(filename: str) -> bool:
        """Check if a file should be included based on its extension or filename.

        This is used by both the serialization logic and the push API to ensure
        consistency in which files are included in workflow artifacts.
        """
        if filename in BaseWorkflowDisplay._INCLUDED_FILENAMES:
            return True
        return any(filename.endswith(ext) for ext in BaseWorkflowDisplay._INCLUDED_FILE_EXTENSIONS)

    def _gather_additional_module_files(self, module_path: str) -> Dict[str, str]:
        workflow_module_path = f"{module_path}.workflow"
        workflow_module = importlib.import_module(workflow_module_path)

        workflow_file_path = workflow_module.__file__
        if not workflow_file_path:
            return {}

        module_dir = os.path.dirname(workflow_file_path)
        additional_files: Dict[str, str] = {}

        virtual_finder = self._find_virtual_finder_for_module(module_path)
        if virtual_finder is not None:
            additional_files = self._gather_virtual_files(virtual_finder)
        else:
            additional_files = self._gather_disk_files(module_dir)

        return additional_files

    def _find_virtual_finder_for_module(self, module_path: str) -> Optional[BaseWorkflowFinder]:
        for finder in sys.meta_path:
            if isinstance(finder, BaseWorkflowFinder) and finder.namespace == module_path:
                return finder
        return None

    def _gather_virtual_files(self, finder: BaseWorkflowFinder) -> Dict[str, str]:
        additional_files: Dict[str, str] = {}
        if not hasattr(finder, "loader") or not hasattr(finder.loader, "files"):
            return additional_files

        for relative_path, content in finder.loader.files.items():
            filename = os.path.basename(relative_path)

            if not self.should_include_file(filename):
                continue

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

            additional_files[relative_path] = content

        return additional_files

    def _gather_disk_files(self, module_dir: str) -> Dict[str, str]:
        additional_files: Dict[str, str] = {}

        for root, _, filenames in os.walk(module_dir):
            for filename in filenames:
                if not self.should_include_file(filename):
                    continue

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
