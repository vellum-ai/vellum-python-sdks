# This file was auto-generated by Fern from our API Definition.

import typing
from .workflow_request_string_input_request import WorkflowRequestStringInputRequest
from .workflow_request_json_input_request import WorkflowRequestJsonInputRequest
from .workflow_request_chat_history_input_request import WorkflowRequestChatHistoryInputRequest
from .workflow_request_number_input_request import WorkflowRequestNumberInputRequest

WorkflowRequestInputRequest = typing.Union[
    WorkflowRequestStringInputRequest,
    WorkflowRequestJsonInputRequest,
    WorkflowRequestChatHistoryInputRequest,
    WorkflowRequestNumberInputRequest,
]