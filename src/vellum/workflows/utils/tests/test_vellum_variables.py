import pytest
from datetime import datetime
from typing import List, Optional, Union

from vellum import (
    ArrayChatMessageContentItem,
    ChatMessage,
    SearchResult,
    VellumAudio,
    VellumDocument,
    VellumImage,
    VellumValue,
)
import vellum.client.types as vellum_types
from vellum.workflows.types.core import Json
from vellum.workflows.utils.vellum_variables import (
    _is_vellum_value_subtype,
    primitive_type_to_vellum_variable_type,
    vellum_variable_type_to_openapi_type,
)


@pytest.mark.parametrize(
    "type_, expected",
    [
        (str, "STRING"),
        (Optional[str], "STRING"),
        (datetime, "STRING"),
        (Optional[datetime], "STRING"),
        (int, "NUMBER"),
        (Optional[int], "NUMBER"),
        (float, "NUMBER"),
        (Optional[float], "NUMBER"),
        (List[ChatMessage], "CHAT_HISTORY"),
        (Optional[List[ChatMessage]], "CHAT_HISTORY"),
        (List[SearchResult], "SEARCH_RESULTS"),
        (Optional[List[SearchResult]], "SEARCH_RESULTS"),
        (Json, "JSON"),
        (Optional[Json], "JSON"),
        (VellumDocument, "DOCUMENT"),
        (Optional[VellumDocument], "DOCUMENT"),
        (VellumAudio, "AUDIO"),
        (Optional[VellumAudio], "AUDIO"),
        (VellumImage, "IMAGE"),
        (Optional[VellumImage], "IMAGE"),
        (list[ChatMessage], "CHAT_HISTORY"),
        (Optional[list[ChatMessage]], "CHAT_HISTORY"),
        (list[SearchResult], "SEARCH_RESULTS"),
        (Optional[list[SearchResult]], "SEARCH_RESULTS"),
        (list[VellumValue], "ARRAY"),
        (Optional[list[VellumValue]], "ARRAY"),
        (List[ArrayChatMessageContentItem], "ARRAY"),
        (Optional[List[ArrayChatMessageContentItem]], "ARRAY"),
    ],
)
def test_primitive_type_to_vellum_variable_type(type_, expected):
    assert primitive_type_to_vellum_variable_type(type_) == expected


@pytest.mark.parametrize(
    "vellum_type, expected",
    [
        ("STRING", "string"),
        ("NUMBER", "number"),
        ("JSON", "object"),
        ("CHAT_HISTORY", "array"),
        ("SEARCH_RESULTS", "array"),
        ("ERROR", "object"),
        ("ARRAY", "array"),
        ("FUNCTION_CALL", "object"),
        ("IMAGE", "object"),
        ("AUDIO", "object"),
        ("DOCUMENT", "object"),
        ("NULL", "null"),
    ],
)
def test_vellum_variable_type_to_openapi_type(vellum_type, expected):
    assert vellum_variable_type_to_openapi_type(vellum_type) == expected


class _SomeType:
    pass


_STRING_OR_NUMBER_VELLUM_VALUE = Union[vellum_types.StringVellumValue, vellum_types.NumberVellumValue]


@pytest.mark.parametrize(
    ["type_", "expected_is_vellum_value_subtype"],
    [
        # Individual union members
        (vellum_types.StringVellumValue, True),
        (vellum_types.NumberVellumValue, True),
        (vellum_types.JsonVellumValue, True),
        (vellum_types.AudioVellumValue, True),
        (vellum_types.VideoVellumValue, True),
        (vellum_types.ImageVellumValue, True),
        (vellum_types.DocumentVellumValue, True),
        (vellum_types.FunctionCallVellumValue, True),
        (vellum_types.ErrorVellumValue, True),
        (vellum_types.ArrayVellumValue, True),
        (vellum_types.ChatHistoryVellumValue, True),
        (vellum_types.SearchResultsVellumValue, True),
        (vellum_types.ThinkingVellumValue, True),
        # Misc union types
        (Union[vellum_types.StringVellumValue, vellum_types.NumberVellumValue], True),
        (_STRING_OR_NUMBER_VELLUM_VALUE, True),
        (Union[vellum_types.StringVellumValue], True),
        (Union["vellum_types.StringVellumValue"], False),
        # Random types
        (int, False),
        (_SomeType, False),
        (List[int], False),
        (Union[int, str], False),
        (Optional[int], False),
        (List["_SomeType"], False),
        # Handle non-types gracefully
        (1, False),
        (_SomeType(), False),
    ],
)
def test_is_vellum_value_subtype(type_, expected_is_vellum_value_subtype):
    assert _is_vellum_value_subtype(type_) == expected_is_vellum_value_subtype
