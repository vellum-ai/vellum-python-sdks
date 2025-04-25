import types
from typing import TYPE_CHECKING, Generic, Optional, Type, TypeVar

from vellum.client import Vellum as VellumClient
from vellum.workflows.types.generics import WorkflowType
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.registry import get_from_workflow_display_registry

if TYPE_CHECKING:
    from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay


def _get_workflow_display_class(*, workflow_class: Type[WorkflowType]) -> Type["BaseWorkflowDisplay"]:
    workflow_display_class = get_from_workflow_display_registry(workflow_class)
    if workflow_display_class:
        return workflow_display_class

    base_workflow_display_class = _get_workflow_display_class(
        workflow_class=workflow_class.__bases__[0],
    )

    # mypy gets upset at dynamic TypeVar's, but it's technically allowed by python
    _WorkflowClassType = TypeVar(f"_{workflow_class.__name__}Type", bound=workflow_class)  # type: ignore[misc]
    # `base_workflow_display_class` is always a Generic class, so it's safe to index into it
    WorkflowDisplayBaseClass = base_workflow_display_class[_WorkflowClassType]  # type: ignore[index]

    WorkflowDisplayClass = types.new_class(
        f"{workflow_class.__name__}Display",
        bases=(WorkflowDisplayBaseClass, Generic[_WorkflowClassType]),
    )

    return WorkflowDisplayClass


def get_workflow_display(
    *,
    workflow_class: Type[WorkflowType],
    parent_display_context: Optional[WorkflowDisplayContext] = None,
    client: Optional[VellumClient] = None,
    dry_run: bool = False,
    # DEPRECATED: The following arguments will be removed in 0.15.0
    root_workflow_class: Optional[Type[WorkflowType]] = None,
    base_display_class: Optional[Type["BaseWorkflowDisplay"]] = None,
) -> "BaseWorkflowDisplay":
    return _get_workflow_display_class(workflow_class=workflow_class)(
        parent_display_context=parent_display_context,
        client=client,
        dry_run=dry_run,
    )
