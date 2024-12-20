from typing import TYPE_CHECKING, Type

from vellum.workflows.events.types import VellumCodeResourceDefinition

if TYPE_CHECKING:
    from vellum.workflows.events.workflow import WorkflowEvent
    from vellum.workflows.workflows.base import BaseWorkflow


def workflow_event_filter(workflow_definition: Type["BaseWorkflow"], event: "WorkflowEvent") -> bool:
    """
    Filters for only Workflow events that were emitted by the `workflow_definition` parameter.
    """

    if (
        event.name == "workflow.execution.initiated"
        or event.name == "workflow.execution.resumed"
        or event.name == "workflow.execution.fulfilled"
        or event.name == "workflow.execution.rejected"
        or event.name == "workflow.execution.paused"
        or event.name == "workflow.execution.streaming"
    ):
        return event.workflow_definition == workflow_definition

    return False


def root_workflow_event_filter(workflow_definition: Type["BaseWorkflow"], event: "WorkflowEvent") -> bool:
    """
    Filters for Workflow and Node events that were emitted by the `workflow_definition` parameter.
    """

    if (
        event.name == "workflow.execution.initiated"
        or event.name == "workflow.execution.resumed"
        or event.name == "workflow.execution.fulfilled"
        or event.name == "workflow.execution.rejected"
        or event.name == "workflow.execution.paused"
        or event.name == "workflow.execution.streaming"
    ):
        return event.workflow_definition == workflow_definition

    if not event.parent:
        return False

    if event.parent.type != "WORKFLOW":
        return False

    event_parent_definition = event.parent.workflow_definition
    current_workflow_definition = VellumCodeResourceDefinition.encode(workflow_definition)

    return event_parent_definition.model_dump() == current_workflow_definition.model_dump()


def all_workflow_event_filter(workflow_definition: Type["BaseWorkflow"], event: "WorkflowEvent") -> bool:
    return True
