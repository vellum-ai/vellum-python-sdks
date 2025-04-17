from typing import TYPE_CHECKING, Dict, Optional, Type

from vellum.workflows.nodes import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow

if TYPE_CHECKING:
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
    from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


# Used to store the mapping between workflows and their display classes
_workflow_display_registry: Dict[Type[BaseWorkflow], Type["BaseWorkflowDisplay"]] = {}

# Used to store the mapping between node types and their display classes
_node_display_registry: Dict[Type[BaseNode], Type["BaseNodeDisplay"]] = {}


def get_from_workflow_display_registry(workflow_class: Type[BaseWorkflow]) -> Optional[Type["BaseWorkflowDisplay"]]:
    return _workflow_display_registry.get(workflow_class)


def register_workflow_display_class(
    workflow_class: Type[BaseWorkflow], workflow_display_class: Type["BaseWorkflowDisplay"]
) -> None:
    _workflow_display_registry[workflow_class] = workflow_display_class


def get_default_workflow_display_class() -> Type["BaseWorkflowDisplay"]:
    return _workflow_display_registry[BaseWorkflow]


def get_from_node_display_registry(node_class: Type[BaseNode]) -> Optional[Type["BaseNodeDisplay"]]:
    return _node_display_registry.get(node_class)


def register_node_display_class(node_class: Type[BaseNode], node_display_class: Type["BaseNodeDisplay"]) -> None:
    _node_display_registry[node_class] = node_display_class
