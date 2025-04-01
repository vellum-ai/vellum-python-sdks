# This file was auto-generated by Fern from our API Definition.

import typing
from .code_execution_node_string_result import CodeExecutionNodeStringResult
from .code_execution_node_number_result import CodeExecutionNodeNumberResult
from .code_execution_node_json_result import CodeExecutionNodeJsonResult
from .code_execution_node_chat_history_result import CodeExecutionNodeChatHistoryResult
from .code_execution_node_search_results_result import CodeExecutionNodeSearchResultsResult
from .code_execution_node_error_result import CodeExecutionNodeErrorResult
from .code_execution_node_array_result import CodeExecutionNodeArrayResult
from .code_execution_node_function_call_result import CodeExecutionNodeFunctionCallResult

CodeExecutionNodeResultOutput = typing.Union[
    CodeExecutionNodeStringResult,
    CodeExecutionNodeNumberResult,
    CodeExecutionNodeJsonResult,
    CodeExecutionNodeChatHistoryResult,
    CodeExecutionNodeSearchResultsResult,
    CodeExecutionNodeErrorResult,
    CodeExecutionNodeArrayResult,
    CodeExecutionNodeFunctionCallResult,
]
