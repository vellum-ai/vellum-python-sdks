from vellum.workflows.events.workflow import WorkflowExecutionInitiatedEvent
from vellum_ee.workflows.display.utils.registry import (
    get_parent_display_context_from_event,
    register_workflow_display_class,
    register_workflow_display_context,
)
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def _should_mark_workflow_dynamic(event: WorkflowExecutionInitiatedEvent) -> bool:
    """
    Check if workflow should be marked as dynamic based on execution context.
    Returns True if parent.type == WORKFLOW_RELEASE_TAG and parent.parent.type == WORKFLOW_NODE.
    """
    if not event.parent:
        return False

    parent = event.parent
    if parent.type != "WORKFLOW_RELEASE_TAG":
        return False

    if not parent.parent or parent.parent.type != "WORKFLOW_NODE":
        return False

    return True


def event_enricher(event: WorkflowExecutionInitiatedEvent) -> WorkflowExecutionInitiatedEvent:
    if event.name != "workflow.execution.initiated":
        return event

    workflow_definition = event.body.workflow_definition
    workflow_display = get_workflow_display(
        workflow_class=workflow_definition,
        parent_display_context=get_parent_display_context_from_event(event),
        dry_run=True,
    )
    register_workflow_display_context(event.span_id, workflow_display.display_context)
    event.body.display_context = workflow_display.get_event_display_context()

    if event.body.workflow_definition.is_dynamic or _should_mark_workflow_dynamic(event):
        register_workflow_display_class(workflow_definition, workflow_display.__class__)
        workflow_version_exec_config = workflow_display.serialize()
        setattr(event.body, "workflow_version_exec_config", workflow_version_exec_config)

    return event
