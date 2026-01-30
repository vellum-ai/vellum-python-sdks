from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Tuple, Type

from vellum.client import Vellum as VellumClient
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.events.workflow import WorkflowEventDisplayContext  # noqa: F401
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, StateValueReference, WorkflowInputReference
from vellum.workflows.types.core import JsonObject
from vellum.workflows.vellum_client import create_vellum_client
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    StateValueDisplay,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay
from vellum_ee.workflows.display.utils.dependencies import MLModel
from vellum_ee.workflows.display.utils.registry import get_default_workflow_display_class

if TYPE_CHECKING:
    from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay


WorkflowInputsDisplays = Dict[WorkflowInputReference, WorkflowInputsDisplay]
StateValueDisplays = Dict[StateValueReference, StateValueDisplay]
NodeDisplays = Dict[Type[BaseNode], BaseNodeDisplay]
NodeOutputDisplays = Dict[OutputReference, NodeOutputDisplay]
EntrypointDisplays = Dict[Type[BaseNode], EntrypointDisplay]
WorkflowOutputDisplays = Dict[BaseDescriptor, WorkflowOutputDisplay]
EdgeDisplays = Dict[Tuple[Port, Type[BaseNode]], EdgeDisplay]
PortDisplays = Dict[Port, PortDisplay]


@dataclass
class WorkflowDisplayContext:
    client: VellumClient = field(default_factory=create_vellum_client)
    workflow_display_class: Type["BaseWorkflowDisplay"] = field(default_factory=get_default_workflow_display_class)
    workflow_display: WorkflowMetaDisplay = field(default_factory=lambda: WorkflowMetaDisplay.get_default(BaseWorkflow))
    workflow_input_displays: WorkflowInputsDisplays = field(default_factory=dict)
    global_workflow_input_displays: WorkflowInputsDisplays = field(default_factory=dict)
    state_value_displays: StateValueDisplays = field(default_factory=dict)
    global_state_value_displays: StateValueDisplays = field(default_factory=dict)
    node_displays: NodeDisplays = field(default_factory=dict)
    global_node_displays: NodeDisplays = field(default_factory=dict)
    global_node_output_displays: NodeOutputDisplays = field(default_factory=dict)
    entrypoint_displays: EntrypointDisplays = field(default_factory=dict)
    workflow_output_displays: WorkflowOutputDisplays = field(default_factory=dict)
    edge_displays: EdgeDisplays = field(default_factory=dict)
    port_displays: PortDisplays = field(default_factory=dict)
    dry_run: bool = False
    ml_models: List[MLModel] = field(default_factory=list)
    _dependencies: Dict[str, JsonObject] = field(default_factory=dict)
    _errors: List[Exception] = field(default_factory=list)
    _invalid_nodes: List[Type[BaseNode]] = field(default_factory=list)

    def add_dependency(self, dependency: JsonObject) -> None:
        """Register a dependency. Deduplicates by type and relevant identifying fields."""
        dep_type = dependency.get("type")
        if dep_type == "MODEL_PROVIDER":
            key = f"MODEL_PROVIDER:{dependency.get('model_name')}"
        elif dep_type == "INTEGRATION":
            key = f"INTEGRATION:{dependency.get('provider')}:{dependency.get('name')}"
        else:
            key = f"{dep_type}:{dependency.get('name')}"
        if key not in self._dependencies:
            self._dependencies[key] = dependency

    def get_dependencies(self) -> List[JsonObject]:
        """Get all registered dependencies."""
        return list(self._dependencies.values())

    @cached_property
    def ml_models_map(self) -> Dict[str, MLModel]:
        """Get a map of model names to MLModel instances for O(1) lookup."""
        return {model.name: model for model in self.ml_models}

    def add_error(self, error: Exception, node: Optional[Type[BaseNode]] = None) -> None:
        if self.dry_run:
            self._errors.append(error)
            return

        raise error

    def add_validation_error(self, error: Exception) -> None:
        self._errors.append(error)

    def add_invalid_node(self, node: Type[BaseNode]) -> None:
        """Track a node that failed to serialize."""
        if node not in self._invalid_nodes:
            self._invalid_nodes.append(node)

    @property
    def errors(self) -> Iterator[Exception]:
        return iter(self._errors)

    @property
    def invalid_nodes(self) -> Iterator[Type[BaseNode]]:
        """Get an iterator over nodes that failed to serialize."""
        return iter(self._invalid_nodes)
