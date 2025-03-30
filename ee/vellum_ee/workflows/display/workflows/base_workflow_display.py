from abc import abstractmethod
from copy import copy
from functools import cached_property
import importlib
import logging
from uuid import UUID
from typing import Any, Dict, Generic, Iterator, List, Optional, Tuple, Type, Union, get_args

from vellum.workflows import BaseWorkflow
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.edges import Edge
from vellum.workflows.events.workflow import NodeEventDisplayContext, WorkflowEventDisplayContext
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.utils import get_unadorned_node, get_wrapped_node
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, WorkflowInputReference
from vellum.workflows.types.core import JsonObject
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    StateValueDisplay,
    WorkflowInputsDisplayOverridesType,
    WorkflowInputsDisplayType,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
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
    WorkflowOutputDisplays,
)
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

logger = logging.getLogger(__name__)


class BaseWorkflowDisplay(
    Generic[
        WorkflowType,
        WorkflowInputsDisplayType,
        WorkflowInputsDisplayOverridesType,
    ]
):
    # Used to specify the display data for a workflow.
    workflow_display: Optional[WorkflowMetaDisplay] = None

    # Used to explicitly specify display data for a workflow's inputs.
    inputs_display: Dict[WorkflowInputReference, WorkflowInputsDisplayOverridesType] = {}

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

    # Used to store the mapping between workflows and their display classes
    _workflow_display_registry: Dict[Type[WorkflowType], Type["BaseWorkflowDisplay"]] = {}

    _errors: List[Exception]

    _dry_run: bool

    def __init__(
        self,
        workflow: Type[WorkflowType],
        *,
        parent_display_context: Optional[WorkflowDisplayContext[WorkflowInputsDisplayType,]] = None,
        dry_run: bool = False,
    ):
        self._workflow = workflow
        self._parent_display_context = parent_display_context
        self._errors: List[Exception] = []
        self._dry_run = dry_run

    @abstractmethod
    def serialize(self) -> JsonObject:
        pass

    @classmethod
    def get_from_workflow_display_registry(cls, workflow_class: Type[WorkflowType]) -> Type["BaseWorkflowDisplay"]:
        try:
            return cls._workflow_display_registry[workflow_class]
        except KeyError:
            return cls._workflow_display_registry[WorkflowType]  # type: ignore [misc]

    @cached_property
    def workflow_id(self) -> UUID:
        """Can be overridden as a class attribute to specify a custom workflow id."""
        return uuid4_from_hash(self._workflow.__qualname__)

    @property
    @abstractmethod
    def node_display_base_class(self) -> Type[BaseNodeDisplay]:
        pass

    def add_error(self, error: Exception) -> None:
        if self._dry_run:
            self._errors.append(error)
            return

        raise error

    @property
    def errors(self) -> Iterator[Exception]:
        return iter(self._errors)

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
        node_display_class = get_node_display_class(self.node_display_base_class, node)
        node_display = node_display_class()

        if not isinstance(node_display, self.node_display_base_class):
            raise ValueError(f"{node.__name__} must be a subclass of {self.node_display_base_class.__name__}")

        return node_display

    @cached_property
    def display_context(
        self,
    ) -> WorkflowDisplayContext[WorkflowInputsDisplayType]:
        workflow_meta_display = self._generate_workflow_meta_display()

        global_node_output_displays: NodeOutputDisplays = (
            copy(self._parent_display_context.global_node_output_displays) if self._parent_display_context else {}
        )

        node_displays: NodeDisplays = {}

        global_node_displays: NodeDisplays = (
            copy(self._parent_display_context.global_node_displays) if self._parent_display_context else {}
        )

        port_displays: PortDisplays = {}

        for node in self._workflow.get_nodes():
            self._enrich_node_displays(
                node=node,
                node_displays=node_displays,
                global_node_displays=global_node_displays,
                global_node_output_displays=global_node_output_displays,
                port_displays=port_displays,
            )

        for node in self._workflow.get_unused_nodes():
            self._enrich_node_displays(
                node=node,
                node_displays=node_displays,
                global_node_displays=global_node_displays,
                global_node_output_displays=global_node_output_displays,
                port_displays=port_displays,
            )

        workflow_input_displays: Dict[WorkflowInputReference, WorkflowInputsDisplayType] = {}
        # If we're dealing with a nested workflow, then it should have access to the inputs of its parents.
        global_workflow_input_displays = (
            copy(self._parent_display_context.workflow_input_displays) if self._parent_display_context else {}
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
                workflow_output_display or self._generate_workflow_output_display(workflow_output)
            )

        return WorkflowDisplayContext(
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

        entrypoint_node_id = uuid4_from_hash(f"{self.workflow_id}|entrypoint_node_id")
        entrypoint_node_source_handle_id = uuid4_from_hash(f"{self.workflow_id}|entrypoint_node_source_handle_id")

        return WorkflowMetaDisplay(
            entrypoint_node_id=entrypoint_node_id,
            entrypoint_node_source_handle_id=entrypoint_node_source_handle_id,
            entrypoint_node_display=NodeDisplayData(),
        )

    @abstractmethod
    def _generate_workflow_input_display(
        self, workflow_input: WorkflowInputReference, overrides: Optional[WorkflowInputsDisplayOverridesType] = None
    ) -> WorkflowInputsDisplayType:
        pass

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

    def _generate_workflow_output_display(self, output: BaseDescriptor) -> WorkflowOutputDisplay:
        output_id = uuid4_from_hash(f"{self.workflow_id}|id|{output.name}")

        return WorkflowOutputDisplay(id=output_id, name=output.name)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        workflow_class = get_args(cls.__orig_bases__[0])[0]  # type: ignore [attr-defined]
        cls._workflow_display_registry[workflow_class] = cls

    @staticmethod
    def gather_event_display_context(
        module_path: str, workflow_class: Type[BaseWorkflow]
    ) -> Union[WorkflowEventDisplayContext, None]:
        workflow_display_module = f"{module_path}.display.workflow"
        try:
            display_class = importlib.import_module(workflow_display_module)
        except ModuleNotFoundError:
            return None

        workflow_display = display_class.WorkflowDisplay(workflow_class)
        if not isinstance(workflow_display, BaseWorkflowDisplay):
            return None

        return workflow_display.get_event_display_context()

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
            input_display = {}
            if isinstance(current_node_display, BaseNodeVellumDisplay):
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
