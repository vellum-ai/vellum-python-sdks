import pytest
from typing import List, Optional

from vellum import ChatMessage, SearchResult, VellumAudio, VellumDocument, VellumImage
from vellum.workflows.types.core import Json
from vellum.workflows.utils.vellum_variables import (
    primitive_type_to_vellum_variable_type,
    vellum_variable_type_to_openapi_type,
)


@pytest.mark.parametrize(
    "type_, expected",
    [
        (str, "STRING"),
        (Optional[str], "STRING"),
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
