# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
import typing
from .string_variable_value import StringVariableValue
from .number_variable_value import NumberVariableValue
from .json_variable_value import JsonVariableValue
from .error_variable_value import ErrorVariableValue
from .function_call_variable_value import FunctionCallVariableValue
from .image_variable_value import ImageVariableValue
from .audio_variable_value import AudioVariableValue
from .chat_history_variable_value import ChatHistoryVariableValue
from .search_results_variable_value import SearchResultsVariableValue
import typing

if typing.TYPE_CHECKING:
    from .array_variable_value import ArrayVariableValue
ArrayVariableValueItem = typing.Union[
    StringVariableValue,
    NumberVariableValue,
    JsonVariableValue,
    ErrorVariableValue,
    FunctionCallVariableValue,
    ImageVariableValue,
    AudioVariableValue,
    ChatHistoryVariableValue,
    SearchResultsVariableValue,
    "ArrayVariableValue",
]
