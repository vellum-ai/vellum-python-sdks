from enum import Enum
from typing import (  # type: ignore[attr-defined]
    Any,
    Dict,
    List,
    Union,
    _GenericAlias,
    _SpecialGenericAlias,
    _UnionGenericAlias,
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


EntityInputsInterface = Dict[str, Any]


class MergeBehavior(Enum):
    AWAIT_ALL = "AWAIT_ALL"
    AWAIT_ANY = "AWAIT_ANY"
    AWAIT_ATTRIBUTES = "AWAIT_ATTRIBUTES"


class ConditionType(Enum):
    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
