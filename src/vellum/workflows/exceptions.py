from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from vellum.workflows.errors import WorkflowError, WorkflowErrorCode

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow


class NodeException(Exception):
    def __init__(
        self,
        message: str,
        code: WorkflowErrorCode = WorkflowErrorCode.INTERNAL_ERROR,
        raw_data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.raw_data = raw_data
        super().__init__(message)

    @property
    def error(self) -> WorkflowError:
        return WorkflowError(
            message=self.message,
            code=self.code,
            raw_data=self.raw_data,
        )

    @staticmethod
    def of(workflow_error: WorkflowError) -> "NodeException":
        return NodeException(message=workflow_error.message, code=workflow_error.code, raw_data=workflow_error.raw_data)


class WorkflowInitializationException(Exception):
    def __init__(
        self,
        message: str,
        workflow_definition: Type["BaseWorkflow"],
        code: WorkflowErrorCode = WorkflowErrorCode.INVALID_INPUTS,
    ):
        self.message = message
        self.code = code
        self.definition = workflow_definition
        super().__init__(message)

    @property
    def error(self) -> WorkflowError:
        return WorkflowError(
            message=self.message,
            code=self.code,
        )
