import importlib
import re
import types
from typing import TYPE_CHECKING, Generic, Optional, Type, TypeVar

from vellum.client import Vellum as VellumClient
from vellum.workflows import BaseWorkflow
from vellum.workflows.types.generics import WorkflowType
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.registry import get_from_workflow_display_registry

if TYPE_CHECKING:
    from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay


def _ensure_display_module_imported(workflow_class: Type[WorkflowType]) -> None:
    """
    Best-effort import of the workflow's display module to ensure any custom
    WorkflowDisplay subclass is registered before we look it up in the registry.

    This allows workflows to work without a display/__init__.py file that
    re-exports from .workflow and .nodes.
    """
    module_name = workflow_class.__module__

    if module_name == BaseWorkflow.__module__:
        return

    if module_name.endswith(".workflow"):
        root = re.sub(r"\.workflow$", "", module_name)
        display_workflow_module = f"{root}.display.workflow"
        try:
            importlib.import_module(display_workflow_module)
        except ImportError:
            pass


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
    ml_models: Optional[list] = None,
    # DEPRECATED: The following arguments will be removed in 0.15.0
    root_workflow_class: Optional[Type[WorkflowType]] = None,
    base_display_class: Optional[Type["BaseWorkflowDisplay"]] = None,
) -> "BaseWorkflowDisplay":
    _ensure_display_module_imported(workflow_class)
    return _get_workflow_display_class(workflow_class=workflow_class)(
        parent_display_context=parent_display_context,
        client=client,
        dry_run=dry_run,
        ml_models=ml_models,
    )
