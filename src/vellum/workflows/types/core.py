from enum import Enum
from multiprocessing.synchronize import Event as MultiprocessingEvent
from threading import Event as ThreadingEvent
from typing import (  # type: ignore[attr-defined]
    Any,
    Dict,
    Iterable,
    List,
    Union,
    _GenericAlias,
    _SpecialGenericAlias,
    _UnionGenericAlias,
)

from vellum.client.core.pydantic_utilities import UniversalBaseModel

JsonArray = List["Json"]
JsonObject = Dict[str, "Json"]
Json = Union[None, bool, int, float, str, JsonArray, JsonObject]


def is_json_type(types: Iterable) -> bool:
    # Check explicitly for our internal JSON type.
    # Matches the type found at vellum.workflows.types.core.Json
    actual_types_with_explicit_ref = [
        bool,
        int,
        float,
        str,
        List[Json],
        Dict[str, Json],
    ]
    with_none = [type(None), *actual_types_with_explicit_ref]
    types_list = list(types)
    return types_list == actual_types_with_explicit_ref or types_list == with_none


CancelSignal = Union[ThreadingEvent, MultiprocessingEvent]

# Unions and Generics inherit from `_GenericAlias` instead of `type`
# In future versions of python, we'll see `_UnionGenericAlias`
UnderGenericAlias = _GenericAlias
SpecialGenericAlias = _SpecialGenericAlias
UnionGenericAlias = _UnionGenericAlias


class VellumSecret(UniversalBaseModel):
    name: str


EntityInputsInterface = Dict[str, Any]


class MergeBehavior(Enum):
    AWAIT_ALL = "AWAIT_ALL"
    AWAIT_ANY = "AWAIT_ANY"
    AWAIT_ATTRIBUTES = "AWAIT_ATTRIBUTES"
    CUSTOM = "CUSTOM"


class ConditionType(Enum):
    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
