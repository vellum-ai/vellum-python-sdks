from typing import ClassVar, Union

from vellum.client.types.vellum_error import VellumError
from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode, vellum_error_to_workflow_error
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base import BaseNode


class ErrorNode(BaseNode):
    """
    Used to raise an error to reject the surrounding Workflow.

    error: Union[str, VellumError] - The error to raise.
    """

    error: ClassVar[Union[str, WorkflowError, VellumError]]

    def run(self) -> BaseNode.Outputs:
        if isinstance(self.error, str):
            raise NodeException(message=self.error, code=WorkflowErrorCode.USER_DEFINED_ERROR)
        elif isinstance(self.error, WorkflowError):
            raise NodeException(message=self.error.message, code=self.error.code)
        elif isinstance(self.error, VellumError):
            workflow_error = vellum_error_to_workflow_error(self.error)
            raise NodeException(message=workflow_error.message, code=workflow_error.code)
        else:
            raise NodeException(
                message=f"Error node received an unexpected input type: {self.error.__class__}",
                code=WorkflowErrorCode.INVALID_INPUTS,
            )
