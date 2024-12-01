from enum import Enum
from typing import (  # type: ignore[attr-defined]
    Dict,
    List,
    Union,
    _GenericAlias,
    _SpecialGenericAlias,
    _UnionGenericAlias,
)

from vellum import (
    ChatMessage,
    FunctionCall,
    FunctionCallRequest,
    SearchResult,
    SearchResultRequest,
    VellumAudio,
    VellumAudioRequest,
    VellumError,
    VellumErrorRequest,
    VellumImage,
    VellumImageRequest,
    VellumValue,
    VellumValueRequest,
)

JsonArray = List["Json"]
JsonObject = Dict[str, "Json"]
Json = Union[None, bool, int, float, str, JsonArray, JsonObject]

# Unions and Generics inherit from `_GenericAlias` instead of `type`
# In future versions of python, we'll see `_UnionGenericAlias`
UnderGenericAlias = _GenericAlias
SpecialGenericAlias = _SpecialGenericAlias
UnionGenericAlias = _UnionGenericAlias


class VellumSecret:
    name: str

    def __init__(self, name: str):
        self.name = name


VellumValuePrimitive = Union[
    # String inputs
    str,
    # Chat history inputs
    List[ChatMessage],
    List[ChatMessage],
    # Search results inputs
    List[SearchResultRequest],
    List[SearchResult],
    # JSON inputs
    Json,
    # Number inputs
    float,
    # Function Call Inputs
    FunctionCall,
    FunctionCallRequest,
    # Error Inputs
    VellumError,
    VellumErrorRequest,
    # Array Inputs
    List[VellumValueRequest],
    List[VellumValue],
    # Image Inputs
    VellumImage,
    VellumImageRequest,
    # Audio Inputs
    VellumAudio,
    VellumAudioRequest,
    # Vellum Secrets
    VellumSecret,
]

EntityInputsInterface = Dict[
    str,
    VellumValuePrimitive,
]


class MergeBehavior(Enum):
    AWAIT_ALL = "AWAIT_ALL"
    AWAIT_ANY = "AWAIT_ANY"
    AWAIT_ATTRIBUTES = "AWAIT_ATTRIBUTES"

class ConditionType(Enum):
    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
