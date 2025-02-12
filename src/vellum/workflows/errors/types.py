from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from vellum.client.types.vellum_error import VellumError
from vellum.client.types.vellum_error_code_enum import VellumErrorCodeEnum
from vellum.client.types.workflow_event_error import WorkflowEventError
from vellum.client.types.workflow_execution_event_error_code import WorkflowExecutionEventErrorCode


class WorkflowErrorCode(Enum):
    INVALID_WORKFLOW = "INVALID_WORKFLOW"
    INVALID_INPUTS = "INVALID_INPUTS"
    INVALID_OUTPUTS = "INVALID_OUTPUTS"
    INVALID_STATE = "INVALID_STATE"
    INVALID_CODE = "INVALID_CODE"
    INVALID_TEMPLATE = "INVALID_TEMPLATE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NODE_EXECUTION = "NODE_EXECUTION"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    USER_DEFINED_ERROR = "USER_DEFINED_ERROR"
    WORKFLOW_CANCELLED = "WORKFLOW_CANCELLED"


@dataclass(frozen=True)
class WorkflowError:
    message: str
    code: WorkflowErrorCode

    def __contains__(self, item: Any) -> bool:
        return item in self.message


_VELLUM_ERROR_CODE_TO_WORKFLOW_ERROR_CODE: Dict[VellumErrorCodeEnum, WorkflowErrorCode] = {
    "INVALID_REQUEST": WorkflowErrorCode.INVALID_INPUTS,
    "INVALID_INPUTS": WorkflowErrorCode.INVALID_INPUTS,
    "PROVIDER_ERROR": WorkflowErrorCode.PROVIDER_ERROR,
    "REQUEST_TIMEOUT": WorkflowErrorCode.PROVIDER_ERROR,
    "INTERNAL_SERVER_ERROR": WorkflowErrorCode.INTERNAL_ERROR,
    "USER_DEFINED_ERROR": WorkflowErrorCode.USER_DEFINED_ERROR,
}


def vellum_error_to_workflow_error(error: VellumError) -> WorkflowError:
    return WorkflowError(
        message=error.message,
        code=_VELLUM_ERROR_CODE_TO_WORKFLOW_ERROR_CODE.get(error.code, WorkflowErrorCode.INTERNAL_ERROR),
    )


_WORKFLOW_EVENT_ERROR_CODE_TO_WORKFLOW_ERROR_CODE: Dict[WorkflowExecutionEventErrorCode, WorkflowErrorCode] = {
    "WORKFLOW_INITIALIZATION": WorkflowErrorCode.INVALID_WORKFLOW,
    "WORKFLOW_CANCELLED": WorkflowErrorCode.WORKFLOW_CANCELLED,
    "NODE_EXECUTION_COUNT_LIMIT_REACHED": WorkflowErrorCode.INVALID_STATE,
    "INTERNAL_SERVER_ERROR": WorkflowErrorCode.INTERNAL_ERROR,
    "NODE_EXECUTION": WorkflowErrorCode.NODE_EXECUTION,
    "LLM_PROVIDER": WorkflowErrorCode.PROVIDER_ERROR,
    "INVALID_CODE": WorkflowErrorCode.INVALID_CODE,
    "INVALID_TEMPLATE": WorkflowErrorCode.INVALID_TEMPLATE,
    "USER_DEFINED_ERROR": WorkflowErrorCode.USER_DEFINED_ERROR,
}


def workflow_event_error_to_workflow_error(error: WorkflowEventError) -> WorkflowError:
    return WorkflowError(
        message=error.message,
        code=_WORKFLOW_EVENT_ERROR_CODE_TO_WORKFLOW_ERROR_CODE.get(error.code, WorkflowErrorCode.INTERNAL_ERROR),
    )


_WORKFLOW_ERROR_CODE_TO_VELLUM_ERROR_CODE: Dict[WorkflowErrorCode, VellumErrorCodeEnum] = {
    WorkflowErrorCode.INVALID_WORKFLOW: "INVALID_REQUEST",
    WorkflowErrorCode.INVALID_INPUTS: "INVALID_INPUTS",
    WorkflowErrorCode.INVALID_OUTPUTS: "INVALID_REQUEST",
    WorkflowErrorCode.INVALID_STATE: "INVALID_REQUEST",
    WorkflowErrorCode.INVALID_CODE: "INVALID_CODE",
    WorkflowErrorCode.INVALID_TEMPLATE: "INVALID_INPUTS",
    WorkflowErrorCode.INTERNAL_ERROR: "INTERNAL_SERVER_ERROR",
    WorkflowErrorCode.NODE_EXECUTION: "USER_DEFINED_ERROR",
    WorkflowErrorCode.PROVIDER_ERROR: "PROVIDER_ERROR",
    WorkflowErrorCode.USER_DEFINED_ERROR: "USER_DEFINED_ERROR",
    WorkflowErrorCode.WORKFLOW_CANCELLED: "REQUEST_TIMEOUT",
}


def workflow_error_to_vellum_error(error: WorkflowError) -> VellumError:
    return VellumError(
        message=error.message,
        code=_WORKFLOW_ERROR_CODE_TO_VELLUM_ERROR_CODE.get(error.code, "INTERNAL_SERVER_ERROR"),
    )
