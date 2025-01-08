from abc import abstractmethod
from copy import copy
from functools import cached_property
import logging
from uuid import UUID
from typing import Any, Dict, Generic, Iterator, List, Optional, Tuple, Type, get_args

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.edges import Edge
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.utils import get_wrapped_node, has_wrapped_node
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, WorkflowInputReference
from vellum.workflows.types.core import JsonObject
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.base import (
    EdgeDisplayOverridesType,
    EdgeDisplayType,
    EntrypointDisplayOverridesType,
    EntrypointDisplayType,
    WorkflowInputsDisplayOverridesType,
    WorkflowInputsDisplayType,
    WorkflowMetaDisplayOverridesType,
    WorkflowMetaDisplayType,
    WorkflowOutputDisplayOverridesType,
    WorkflowOutputDisplayType,
)
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay, PortDisplayOverrides
from vellum_ee.workflows.display.types import NodeDisplayType, WorkflowDisplayContext

logger = logging.getLogger(__name__)


class BaseWorkflowDisplay(
    Generic[
        WorkflowType,
        WorkflowMetaDisplayType,
        WorkflowMetaDisplayOverridesType,
        WorkflowInputsDisplayType,
        WorkflowInputsDisplayOverridesType,
        NodeDisplayType,
        EntrypointDisplayType,
        EntrypointDisplayOverridesType,
        EdgeDisplayType,
        EdgeDisplayOverridesType,
        WorkflowOutputDisplayType,
        WorkflowOutputDisplayOverridesType,
    ]
):
    # Used to specify the display data for a workflow.
    workflow_display: Optional[WorkflowMetaDisplayOverridesType] = None

    # Used to explicitly specify display data for a workflow's inputs.
    inputs_display: Dict[WorkflowInputReference, WorkflowInputsDisplayOverridesType] = {}

    # Used to explicitly specify display data for a workflow's entrypoints.
    entrypoint_displays: Dict[Type[BaseNode], EntrypointDisplayOverridesType] = {}

    # Used to explicitly specify display data for a workflow's outputs.
    output_displays: Dict[BaseDescriptor, WorkflowOutputDisplayOverridesType] = {}

    # Used to explicitly specify display data for a workflow's edges.
    edge_displays: Dict[Tuple[Port, Type[BaseNode]], EdgeDisplayOverridesType] = {}

    # Used to explicitly specify display data for a workflow's ports.
    port_displays: Dict[Port, PortDisplayOverrides] = {}

    # Used to store the mapping between workflows and their display classes
    _workflow_display_registry: Dict[Type[WorkflowType], Type["BaseWorkflowDisplay"]] = {}

    _errors: List[Exception]

    _dry_run: bool

    def __init__(
        self,
        workflow: Type[WorkflowType],
        *,
        parent_display_context: Optional[
            WorkflowDisplayContext[
                WorkflowMetaDisplayType,
                WorkflowInputsDisplayType,
                NodeDisplayType,
                EntrypointDisplayType,
                WorkflowOutputDisplayType,
                EdgeDisplayType,
            ]
        ] = None,
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
    def node_display_base_class(self) -> Type[NodeDisplayType]:
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
        node_display: NodeDisplayType,
        node_output_displays: Dict[OutputReference, Tuple[Type[BaseNode], NodeOutputDisplay]],
    ):
        """This method recursively adds nodes wrapped in decorators to the node_output_displays dictionary."""

        for node_output in node.Outputs:
            if node_output in node_output_displays:
                continue

            if has_wrapped_node(node):
                inner_node = get_wrapped_node(node)
                if inner_node._is_wrapped_node:
                    inner_node_display = self._get_node_display(inner_node)
                    self._enrich_global_node_output_displays(inner_node, inner_node_display, node_output_displays)

            # TODO: Make sure this output ID matches the workflow output ID of the subworkflow node's workflow
            # https://app.shortcut.com/vellum/story/5660/fix-output-id-in-subworkflow-nodes
            node_output_displays[node_output] = node, node_display.get_node_output_display(node_output)

    def _enrich_node_port_displays(
        self,
        node: Type[BaseNode],
        node_display: NodeDisplayType,
        port_displays: Dict[Port, PortDisplay],
    ):
        """This method recursively adds nodes wrapped in decorators to the port_displays dictionary."""

        for port in node.Ports:
            if port in port_displays:
                continue

            if has_wrapped_node(node):
                inner_node = get_wrapped_node(node)
                if inner_node._is_wrapped_node:
                    inner_node_display = self._get_node_display(inner_node)
                    self._enrich_node_port_displays(inner_node, inner_node_display, port_displays)

            port_displays[port] = node_display.get_node_port_display(port)

    def _get_node_display(self, node: Type[BaseNode]) -> NodeDisplayType:
        node_display_class = get_node_display_class(self.node_display_base_class, node)
        node_display = node_display_class()

        if not isinstance(node_display, self.node_display_base_class):
            raise ValueError(f"{node.__name__} must be a subclass of {self.node_display_base_class.__name__}")

        return node_display

    @cached_property
    def display_context(
        self,
    ) -> WorkflowDisplayContext[
        WorkflowMetaDisplayType,
        WorkflowInputsDisplayType,
        NodeDisplayType,
        EntrypointDisplayType,
        WorkflowOutputDisplayType,
        EdgeDisplayType,
    ]:
        workflow_display = self._generate_workflow_meta_display()

        global_node_output_displays: Dict[OutputReference, Tuple[Type[BaseNode], NodeOutputDisplay]] = (
            copy(self._parent_display_context.global_node_output_displays) if self._parent_display_context else {}
        )

        node_displays: Dict[Type[BaseNode], NodeDisplayType] = {}

        global_node_displays: Dict[Type[BaseNode], NodeDisplayType] = (
            copy(self._parent_display_context.global_node_displays) if self._parent_display_context else {}
        )

        port_displays: Dict[Port, PortDisplay] = {}

        # TODO: We should still serialize nodes that are in the workflow's directory but aren't used in the graph.
        # https://app.shortcut.com/vellum/story/5394
        for node in self._workflow.get_nodes():
            if node in global_node_displays:
                continue
            node_display = self._get_node_display(node)
            node_displays[node] = node_display
            global_node_displays[node] = node_display

            # Nodes wrapped in a decorator need to be in our node display dictionary for later retrieval
            if has_wrapped_node(node):
                inner_node = get_wrapped_node(node)
                inner_node_display = self._get_node_display(inner_node)

                if inner_node._is_wrapped_node:
                    node_displays[inner_node] = inner_node_display
                    global_node_displays[inner_node] = inner_node_display

            self._enrich_global_node_output_displays(node, node_display, global_node_output_displays)
            self._enrich_node_port_displays(node, node_display, port_displays)

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

        entrypoint_displays: Dict[Type[BaseNode], EntrypointDisplayType] = {}
        for entrypoint in self._workflow.get_entrypoints():
            if entrypoint in entrypoint_displays:
                continue

            entrypoint_display_overrides = self.entrypoint_displays.get(entrypoint)
            entrypoint_displays[entrypoint] = self._generate_entrypoint_display(
                entrypoint, workflow_display, node_displays, overrides=entrypoint_display_overrides
            )

        edge_displays: Dict[Tuple[Port, Type[BaseNode]], EdgeDisplayType] = {}
        for edge in self._workflow.get_edges():
            if edge in edge_displays:
                continue

            edge_display_overrides = self.edge_displays.get((edge.from_port, edge.to_node))
            edge_displays[(edge.from_port, edge.to_node)] = self._generate_edge_display(
                edge, node_displays, port_displays, overrides=edge_display_overrides
            )

        workflow_output_displays: Dict[BaseDescriptor, WorkflowOutputDisplayType] = {}
        for workflow_output in self._workflow.Outputs:
            if workflow_output in workflow_output_displays:
                continue

            if not isinstance(workflow_output, OutputReference):
                raise ValueError(f"{workflow_output} must be an {OutputReference.__name__}")

            if not workflow_output.instance or not isinstance(
                workflow_output.instance, (OutputReference, CoalesceExpression)
            ):
                raise ValueError("Expected to find a descriptor instance on the workflow output")

            workflow_output_display_overrides = self.output_displays.get(workflow_output)
            workflow_output_displays[workflow_output] = self._generate_workflow_output_display(
                workflow_output, overrides=workflow_output_display_overrides
            )

        return WorkflowDisplayContext(
            workflow_display=workflow_display,
            workflow_input_displays=workflow_input_displays,
            global_workflow_input_displays=global_workflow_input_displays,
            node_displays=node_displays,
            global_node_output_displays=global_node_output_displays,
            global_node_displays=global_node_displays,
            entrypoint_displays=entrypoint_displays,
            workflow_output_displays=workflow_output_displays,
            edge_displays=edge_displays,
            port_displays=port_displays,
            workflow_display_class=self.__class__,
        )

    @abstractmethod
    def _generate_workflow_meta_display(self) -> WorkflowMetaDisplayType:
        pass

    @abstractmethod
    def _generate_workflow_input_display(
        self, workflow_input: WorkflowInputReference, overrides: Optional[WorkflowInputsDisplayOverridesType] = None
    ) -> WorkflowInputsDisplayType:
        pass

    @abstractmethod
    def _generate_entrypoint_display(
        self,
        entrypoint: Type[BaseNode],
        workflow_display: WorkflowMetaDisplayType,
        node_displays: Dict[Type[BaseNode], NodeDisplayType],
        overrides: Optional[EntrypointDisplayOverridesType] = None,
    ) -> EntrypointDisplayType:
        pass

    @abstractmethod
    def _generate_workflow_output_display(
        self,
        output: BaseDescriptor,
        overrides: Optional[WorkflowOutputDisplayOverridesType] = None,
    ) -> WorkflowOutputDisplayType:
        pass

    @abstractmethod
    def _generate_edge_display(
        self,
        edge: Edge,
        node_displays: Dict[Type[BaseNode], NodeDisplayType],
        port_displays: Dict[Port, PortDisplay],
        overrides: Optional[EdgeDisplayOverridesType] = None,
    ) -> EdgeDisplayType:
        pass

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        workflow_class = get_args(cls.__orig_bases__[0])[0]  # type: ignore [attr-defined]
        cls._workflow_display_registry[workflow_class] = cls
