import typing
from typing import List, Tuple, Type, Union, get_args, get_origin

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
)
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.types.core import Json


def primitive_type_to_vellum_variable_type(type_: Union[Type, BaseDescriptor]) -> VellumVariableType:
    """Converts a python primitive to a VellumVariableType"""
    if isinstance(type_, BaseDescriptor):
        # Ignore None because those just make types optional
        types = [t for t in type_.types if t is not type(None)]

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
            raise ValueError(f"Expected Descriptor to only have one type, got {types}")

        type_ = type_.types[0]

    if _is_type_optionally_equal(type_, str):
        return "STRING"
    elif _is_type_optionally_in(type_, (int, float)):
        return "NUMBER"
    elif _is_type_optionally_in(type_, (FunctionCall, FunctionCallRequest)):
        return "FUNCTION_CALL"
    elif _is_type_optionally_in(type_, (VellumImage, VellumImageRequest)):
        return "IMAGE"
    elif _is_type_optionally_in(type_, (VellumAudio, VellumAudioRequest)):
        return "AUDIO"
    elif _is_type_optionally_in(type_, (VellumDocument, VellumDocumentRequest)):
        return "DOCUMENT"
    elif _is_type_optionally_in(type_, (VellumError, VellumErrorRequest)):
        return "ERROR"
    elif _is_type_optionally_in(type_, (List[ChatMessage], List[ChatMessageRequest])):
        return "CHAT_HISTORY"
    elif _is_type_optionally_in(type_, (List[SearchResult], List[SearchResultRequest])):
        return "SEARCH_RESULTS"
    elif _is_type_optionally_in(type_, (List[VellumValue], List[VellumValueRequest])):
        return "ARRAY"

    return "JSON"


def _is_type_optionally_equal(type_: Type, target_type: Type) -> bool:
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


def _is_type_optionally_in(type_: Type, target_types: Tuple[Type, ...]) -> bool:
    return any(_is_type_optionally_equal(type_, target_type) for target_type in target_types)
