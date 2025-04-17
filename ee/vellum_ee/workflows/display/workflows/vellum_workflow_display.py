from typing import Generic

from vellum.workflows.types.generics import WorkflowType
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


# DEPRECATED: Use BaseWorkflowDisplay instead - This file will be removed in 0.15.0
class VellumWorkflowDisplay(BaseWorkflowDisplay[WorkflowType], Generic[WorkflowType]):
    pass
