# This file was auto-generated by Fern from our API Definition.

import typing
from .named_test_case_string_variable_value import NamedTestCaseStringVariableValue
from .named_test_case_number_variable_value import NamedTestCaseNumberVariableValue
from .named_test_case_json_variable_value import NamedTestCaseJsonVariableValue
from .named_test_case_chat_history_variable_value import NamedTestCaseChatHistoryVariableValue
from .named_test_case_search_results_variable_value import NamedTestCaseSearchResultsVariableValue
from .named_test_case_error_variable_value import NamedTestCaseErrorVariableValue
from .named_test_case_function_call_variable_value import NamedTestCaseFunctionCallVariableValue
from .named_test_case_array_variable_value import NamedTestCaseArrayVariableValue

NamedTestCaseVariableValue = typing.Union[
    NamedTestCaseStringVariableValue,
    NamedTestCaseNumberVariableValue,
    NamedTestCaseJsonVariableValue,
    NamedTestCaseChatHistoryVariableValue,
    NamedTestCaseSearchResultsVariableValue,
    NamedTestCaseErrorVariableValue,
    NamedTestCaseFunctionCallVariableValue,
    NamedTestCaseArrayVariableValue,
]