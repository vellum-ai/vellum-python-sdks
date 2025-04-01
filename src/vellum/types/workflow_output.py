# This file was auto-generated by Fern from our API Definition.

import typing
from .workflow_output_string import WorkflowOutputString
from .workflow_output_number import WorkflowOutputNumber
from .workflow_output_json import WorkflowOutputJson
from .workflow_output_chat_history import WorkflowOutputChatHistory
from .workflow_output_search_results import WorkflowOutputSearchResults
from .workflow_output_array import WorkflowOutputArray
from .workflow_output_error import WorkflowOutputError
from .workflow_output_function_call import WorkflowOutputFunctionCall
from .workflow_output_image import WorkflowOutputImage

WorkflowOutput = typing.Union[
    WorkflowOutputString,
    WorkflowOutputNumber,
    WorkflowOutputJson,
    WorkflowOutputChatHistory,
    WorkflowOutputSearchResults,
    WorkflowOutputArray,
    WorkflowOutputError,
    WorkflowOutputFunctionCall,
    WorkflowOutputImage,
]
