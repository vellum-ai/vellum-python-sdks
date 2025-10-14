from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from vellum.workflows.errors import WorkflowError, WorkflowErrorCode

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow


def import_workflow_class() -> Type["BaseWorkflow"]:
    """
    Helper function to help avoid circular imports.

    Ideally, we use the one in types.generics, but _that_ causes circular imports
    due to the `src/vellum/workflows/types/definition.py` module's import of `EnvironmentVariableReference`
    """

    from vellum.workflows.workflows import BaseWorkflow

    return BaseWorkflow


class NodeException(Exception):
    def __init__(
        self,
        message: str,
        code: WorkflowErrorCode = WorkflowErrorCode.INTERNAL_ERROR,
        raw_data: Optional[Dict[str, Any]] = None,
        stacktrace: Optional[str] = None,
    ):
        self.message = message
        self.code = code
        self.raw_data = raw_data
        self.stacktrace = stacktrace
        super().__init__(message)

    @property
    def error(self) -> WorkflowError:
        return WorkflowError(
            message=self.message,
            code=self.code,
            raw_data=self.raw_data,
            stacktrace=self.stacktrace,
        )

    @staticmethod
    def of(workflow_error: WorkflowError) -> "NodeException":
        return NodeException(
            message=workflow_error.message,
            code=workflow_error.code,
            raw_data=workflow_error.raw_data,
            stacktrace=workflow_error.stacktrace,
        )


class WorkflowInitializationException(Exception):
    def __init__(
        self,
        message: str,
        workflow_definition: Optional[Type["BaseWorkflow"]] = None,
        code: WorkflowErrorCode = WorkflowErrorCode.INVALID_INPUTS,
        raw_data: Optional[Dict[str, Any]] = None,
    ):

        self.message = message
        self.code = code
        self.raw_data = raw_data
        self.definition = workflow_definition if workflow_definition is not None else import_workflow_class()
        super().__init__(message)

    @property
    def error(self) -> WorkflowError:
        return WorkflowError(
            message=self.message,
            code=self.code,
            raw_data=self.raw_data,
        )
