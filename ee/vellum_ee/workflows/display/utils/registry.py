from uuid import UUID
from typing import TYPE_CHECKING, Dict, Optional, Type

from vellum.workflows.events.types import BaseEvent
from vellum.workflows.nodes import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow

if TYPE_CHECKING:
    from vellum.workflows.events.types import ParentContext
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
    from vellum_ee.workflows.display.types import WorkflowDisplayContext
    from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


# Used to store the mapping between workflows and their display classes
_workflow_display_registry: Dict[Type[BaseWorkflow], Type["BaseWorkflowDisplay"]] = {}

# Used to store the mapping between node types and their display classes
_node_display_registry: Dict[Type[BaseNode], Type["BaseNodeDisplay"]] = {}

# Registry to store active workflow display contexts by span ID for nested workflow inheritance
_active_workflow_display_contexts: Dict[UUID, "WorkflowDisplayContext"] = {}


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


def register_workflow_display_context(span_id: UUID, display_context: "WorkflowDisplayContext") -> None:
    """Register a workflow display context by span ID for nested workflow inheritance."""
    _active_workflow_display_contexts[span_id] = display_context


def _get_parent_display_context_for_span(span_id: UUID) -> Optional["WorkflowDisplayContext"]:
    """Get the parent display context for a given span ID."""
    return _active_workflow_display_contexts.get(span_id)


def get_parent_display_context_from_event(event: BaseEvent) -> Optional["WorkflowDisplayContext"]:
    """Extract parent display context from an event by traversing the parent chain.

    This function traverses up the parent chain starting from the event's parent,
    looking for workflow parents and attempting to get their display context.

    Args:
        event: The event to extract parent display context from

    Returns:
        The parent workflow display context if found, None otherwise
    """
    if not event.parent:
        return None

    current_parent: Optional["ParentContext"] = event.parent
    while current_parent:
        if current_parent.type == "WORKFLOW":
            # Found a parent workflow, try to get its display context
            parent_span_id = current_parent.span_id
            parent_display_context = _get_parent_display_context_for_span(parent_span_id)
            if parent_display_context:
                return parent_display_context
        # Move up the parent chain
        current_parent = current_parent.parent

    return None
