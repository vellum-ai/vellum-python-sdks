import enum
import json
from typing import Any, List, Union, cast

from vellum.client.types.array_vellum_value import ArrayVellumValue
from vellum.client.types.array_vellum_value_request import ArrayVellumValueRequest
from vellum.client.types.audio_vellum_value import AudioVellumValue
from vellum.client.types.audio_vellum_value_request import AudioVellumValueRequest
from vellum.client.types.chat_history_vellum_value import ChatHistoryVellumValue
from vellum.client.types.chat_history_vellum_value_request import ChatHistoryVellumValueRequest
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.error_vellum_value import ErrorVellumValue
from vellum.client.types.error_vellum_value_request import ErrorVellumValueRequest
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_call_vellum_value_request import FunctionCallVellumValueRequest
from vellum.client.types.image_vellum_value import ImageVellumValue
from vellum.client.types.image_vellum_value_request import ImageVellumValueRequest
from vellum.client.types.json_vellum_value import JsonVellumValue
from vellum.client.types.json_vellum_value_request import JsonVellumValueRequest
from vellum.client.types.number_vellum_value import NumberVellumValue
from vellum.client.types.number_vellum_value_request import NumberVellumValueRequest
from vellum.client.types.search_result import SearchResult
from vellum.client.types.search_result_request import SearchResultRequest
from vellum.client.types.search_results_vellum_value import SearchResultsVellumValue
from vellum.client.types.search_results_vellum_value_request import SearchResultsVellumValueRequest
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.string_vellum_value_request import StringVellumValueRequest
from vellum.client.types.vellum_error import VellumError
from vellum.client.types.vellum_value import VellumValue
from vellum.client.types.vellum_value_request import VellumValueRequest
from vellum.workflows.errors.types import WorkflowError, workflow_error_to_vellum_error
from vellum.workflows.state.encoder import DefaultStateEncoder

VELLUM_VALUE_REQUEST_TUPLE = (
    StringVellumValueRequest,
    NumberVellumValueRequest,
    JsonVellumValueRequest,
    ImageVellumValueRequest,
    AudioVellumValueRequest,
    FunctionCallVellumValueRequest,
    ErrorVellumValueRequest,
    ArrayVellumValueRequest,
    ChatHistoryVellumValueRequest,
    SearchResultsVellumValueRequest,
)


def primitive_to_vellum_value(value: Any) -> VellumValue:
    """Converts a python primitive to a VellumValue"""

    if isinstance(value, str):
        return StringVellumValue(value=value)
    elif isinstance(value, enum.Enum):
        return StringVellumValue(value=value.value)
    elif isinstance(value, (int, float)):
        return NumberVellumValue(value=value)
    elif isinstance(value, list) and (
        all(isinstance(message, ChatMessage) for message in value)
        or all(isinstance(message, ChatMessage) for message in value)
    ):
        chat_messages = cast(Union[List[ChatMessage], List[ChatMessage]], value)
        return ChatHistoryVellumValue(value=chat_messages)
    elif isinstance(value, list) and (
        all(isinstance(search_result, SearchResultRequest) for search_result in value)
        or all(isinstance(search_result, SearchResult) for search_result in value)
    ):
        search_results = cast(Union[List[SearchResultRequest], List[SearchResult]], value)
        return SearchResultsVellumValue(value=search_results)
    elif isinstance(value, VellumError):
        return ErrorVellumValue(value=value)
    elif isinstance(value, WorkflowError):
        return ErrorVellumValue(value=workflow_error_to_vellum_error(value))
    elif isinstance(
        value,
        (
            StringVellumValue,
            NumberVellumValue,
            JsonVellumValue,
            ImageVellumValue,
            AudioVellumValue,
            FunctionCallVellumValue,
            ErrorVellumValue,
            ArrayVellumValue,
            ChatHistoryVellumValue,
            SearchResultsVellumValue,
        ),
    ):
        return value
    elif isinstance(
        value,
        VELLUM_VALUE_REQUEST_TUPLE,
    ):
        # This type ignore is safe because consumers of this function won't care the difference between
        # XVellumValue and XVellumValueRequest. Hopefully in the near future, neither will we
        return value  # type: ignore

    try:
        json_value = json.dumps(value, cls=DefaultStateEncoder)
    except json.JSONDecodeError:
        raise ValueError(f"Unsupported variable type: {value.__class__.__name__}")

    return JsonVellumValue(value=json.loads(json_value))


def primitive_to_vellum_value_request(value: Any) -> VellumValueRequest:
    vellum_value = primitive_to_vellum_value(value)
    vellum_value_request_class = next(
        (
            vellum_value_request_class
            for vellum_value_request_class in VELLUM_VALUE_REQUEST_TUPLE
            if vellum_value_request_class.__name__.startswith(vellum_value.__class__.__name__)
        ),
        None,
    )

    if vellum_value_request_class is None:
        raise ValueError(f"Unsupported variable type: {vellum_value.__class__.__name__}")

    return vellum_value_request_class.model_validate(vellum_value.model_dump())
