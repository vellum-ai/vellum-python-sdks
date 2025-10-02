import typing
from typing import Any, List, Tuple, Type, Union, get_args, get_origin

from vellum import (
    ChatMessage,
    ChatMessageRequest,
    FunctionCall,
    FunctionCallRequest,
    SearchResult,
    SearchResultRequest,
    VellumAudio,
    VellumAudioRequest,
    VellumDocument,
    VellumDocumentRequest,
    VellumError,
    VellumErrorRequest,
    VellumImage,
    VellumImageRequest,
    VellumValue,
    VellumValueRequest,
    VellumVariableType,
    VellumVideo,
    VellumVideoRequest,
)
from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.types.core import Json


def primitive_type_to_vellum_variable_type(type_: Union[Type, BaseDescriptor]) -> VellumVariableType:
    """Converts a python primitive to a VellumVariableType"""
    if isinstance(type_, BaseDescriptor):
        # Ignore None and undefined because those just make types optional
        types = []
        for t in type_.types:
            if t is type(None):
                continue
            if t is undefined or t is type(undefined):
                continue
            if get_origin(t) is type and len(get_args(t)) == 1 and get_args(t)[0] is undefined:
                continue
            types.append(t)

        # default to JSON for typevars where the types is empty tuple
        if len(types) == 0:
            return "JSON"

        if len(types) != 1:
            # Check explicitly for our internal JSON type.
            # Matches the type found at vellum.workflows.utils.vellum_variables.Json
            actual_types_with_explicit_ref = [
                bool,
                int,
                float,
                str,
                typing.List[Json],
                typing.Dict[str, Json],
            ]
            if types == actual_types_with_explicit_ref:
                return "JSON"
            # Number now supports float and int
            elif types == [float, int]:
                return "NUMBER"

            collapse_types = _collapse_types(types)
            if len(collapse_types) == 1:
                return primitive_type_to_vellum_variable_type(collapse_types[0])

            raise ValueError(f"Expected Descriptor to only have one type, got {types}")

        type_ = type_.types[0]

    if _is_type_optionally_equal(type_, str):
        return "STRING"
    elif _is_type_optionally_in(type_, (int, float)):
        return "NUMBER"
    elif _is_type_optionally_in(type_, (FunctionCall, FunctionCallRequest)):
        return "FUNCTION_CALL"
    elif _is_type_optionally_in(type_, (VellumAudio, VellumAudioRequest)):
        return "AUDIO"
    elif _is_type_optionally_in(type_, (VellumVideo, VellumVideoRequest)):
        return "VIDEO"
    elif _is_type_optionally_in(type_, (VellumImage, VellumImageRequest)):
        return "IMAGE"
    elif _is_type_optionally_in(type_, (VellumDocument, VellumDocumentRequest)):
        return "DOCUMENT"
    elif _is_type_optionally_in(type_, (VellumError, VellumErrorRequest)):
        return "ERROR"

    if type_ is typing.Any:
        return "JSON"

    builtin_list_type = _builtin_list_to_vellum_type(type_)
    if builtin_list_type:
        return builtin_list_type

    elif _is_type_optionally_in(type_, (List[ChatMessage], List[ChatMessageRequest])):
        return "CHAT_HISTORY"
    elif _is_type_optionally_in(type_, (List[SearchResult], List[SearchResultRequest])):
        return "SEARCH_RESULTS"
    elif _is_type_optionally_in(type_, (List[VellumValue], List[VellumValueRequest])):
        return "ARRAY"

    return "JSON"


def vellum_variable_type_to_openapi_type(vellum_type: VellumVariableType) -> str:
    """Converts a VellumVariableType to a JSON schema primitive type string"""
    if vellum_type == "STRING":
        return "string"
    elif vellum_type == "NUMBER":
        return "number"
    elif vellum_type == "JSON":
        return "object"
    elif vellum_type == "CHAT_HISTORY":
        return "array"
    elif vellum_type == "SEARCH_RESULTS":
        return "array"
    elif vellum_type == "ERROR":
        return "object"
    elif vellum_type == "ARRAY":
        return "array"
    elif vellum_type == "FUNCTION_CALL":
        return "object"
    elif vellum_type == "AUDIO":
        return "object"
    elif vellum_type == "VIDEO":
        return "object"
    elif vellum_type == "IMAGE":
        return "object"
    elif vellum_type == "DOCUMENT":
        return "object"
    elif vellum_type == "NULL":
        return "null"
    else:
        return "object"


def _is_type_optionally_equal(type_: Type, target_type: Any) -> bool:
    if type_ == target_type:
        return True

    origin = get_origin(type_)
    if origin is not Union:
        return False

    args = get_args(type_)
    if len(args) != 2:
        return False

    source_type, none_type = args
    if none_type is not type(None):
        return False

    return _is_type_optionally_equal(source_type, target_type)


def _is_type_optionally_in(type_: Type, target_types: Tuple[Any, ...]) -> bool:
    return any(_is_type_optionally_equal(type_, target_type) for target_type in target_types)


def _collapse_types(types: List[Type]) -> List[Type]:
    """
    Collapses a list of types into a list of types that are not subtypes of each other.
    What remains are the "most specific" types.
    """

    new_types: List[Type] = []
    for target_type in types:
        if any(_is_subtype(source_type, target_type) for source_type in new_types):
            continue

        new_types.append(target_type)

    return new_types


def _is_subtype(source_type: Type, target_type: Type) -> bool:
    """
    Checks if `source_type` is a strict subtype of `target_type`. Meaning all values that are
    of type `source_type` are also of type `target_type`.
    """

    if source_type == target_type:
        return True

    source_origin = get_origin(source_type)
    if source_origin == target_type:
        return True

    return False


def _unwrap_optional(type_: Type) -> Type:
    origin = get_origin(type_)
    if origin is typing.Union:
        args = get_args(type_)
        if len(args) == 2:
            if args[1] is type(None):
                return args[0]
            if args[0] is type(None):
                return args[1]
    return type_


def _builtin_list_to_vellum_type(type_: Type) -> Union[str, None]:
    candidate = _unwrap_optional(type_)
    origin = get_origin(candidate)
    if origin in (list, typing.List):
        args = get_args(candidate)
        if len(args) == 1:
            item_type = args[0]
            if _is_type_optionally_equal(item_type, ChatMessage) or _is_type_optionally_equal(
                item_type, ChatMessageRequest
            ):
                return "CHAT_HISTORY"
            if _is_type_optionally_equal(item_type, SearchResult) or _is_type_optionally_equal(
                item_type, SearchResultRequest
            ):
                return "SEARCH_RESULTS"
            if _is_type_optionally_equal(item_type, VellumValue) or _is_type_optionally_equal(
                item_type, VellumValueRequest
            ):
                return "ARRAY"
    return None
