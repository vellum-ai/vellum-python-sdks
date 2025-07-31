from enum import Enum
from typing import (  # type: ignore[attr-defined]
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Type,
    Union,
    _GenericAlias,
    _SpecialGenericAlias,
    _UnionGenericAlias,
)

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.types.definition import ComposioToolDefinition, DeploymentDefinition, MCPServer

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow


JsonArray = List["Json"]
JsonObject = Dict[str, "Json"]
Json = Union[None, bool, int, float, str, JsonArray, JsonObject]

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


# Type alias for functions that can be called in tool calling nodes
ToolBase = Union[Callable[..., Any], DeploymentDefinition, Type["BaseWorkflow"], ComposioToolDefinition]
Tool = Union[ToolBase, MCPServer]
