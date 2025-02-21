from vellum.workflows.errors import WorkflowError, WorkflowErrorCode


class NodeException(Exception):
    def __init__(self, message: str, code: WorkflowErrorCode = WorkflowErrorCode.INTERNAL_ERROR):
        self.message = message
        self.code = code
        super().__init__(message)

    @property
    def error(self) -> WorkflowError:
        return WorkflowError(
            message=self.message,
            code=self.code,
        )

    @staticmethod
    def of(workflow_error: WorkflowError) -> "NodeException":
        return NodeException(message=workflow_error.message, code=workflow_error.code)


class WorkflowInitializationException(Exception):
    def __init__(self, message: str, code: WorkflowErrorCode = WorkflowErrorCode.INVALID_INPUTS):
        self.message = message
        self.code = code
        super().__init__(message)

    @property
    def error(self) -> WorkflowError:
        return WorkflowError(
            message=self.message,
            code=self.code,
        )

    @staticmethod
    def of(workflow_error: WorkflowError) -> "WorkflowInitializationException":
        return WorkflowInitializationException(message=workflow_error.message, code=workflow_error.code)
