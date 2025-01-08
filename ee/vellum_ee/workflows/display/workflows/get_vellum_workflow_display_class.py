from typing import Optional, Type

from vellum.workflows.types.generics import WorkflowType
from vellum_ee.workflows.display.types import WorkflowDisplayContext, WorkflowDisplayType


def get_workflow_display(
    *,
    base_display_class: Type[WorkflowDisplayType],
    workflow_class: Type[WorkflowType],
    root_workflow_class: Optional[Type[WorkflowType]] = None,
    parent_display_context: Optional[WorkflowDisplayContext] = None,
    dry_run: bool = False,
) -> WorkflowDisplayType:
    try:
        workflow_display_class = base_display_class.get_from_workflow_display_registry(workflow_class)
    except KeyError:
        try:
            return get_workflow_display(
                base_display_class=base_display_class,
                workflow_class=workflow_class.__bases__[0],
                root_workflow_class=workflow_class if root_workflow_class is None else root_workflow_class,
                parent_display_context=parent_display_context,
                dry_run=dry_run,
            )
        except IndexError:
            return base_display_class(workflow_class)

    return workflow_display_class(  # type: ignore[return-value]
        workflow_class,
        parent_display_context=parent_display_context,
        dry_run=dry_run,
    )
