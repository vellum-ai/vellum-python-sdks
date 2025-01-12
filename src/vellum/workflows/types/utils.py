from copy import deepcopy
from datetime import datetime
import importlib
from types import GenericAlias
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from vellum import ArrayVellumValue, ArrayVellumValueRequest, ChatMessagePromptBlock
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.types.core import Json, SpecialGenericAlias, UnderGenericAlias, UnionGenericAlias

_T = TypeVar("_T")
_LHS = TypeVar("_LHS")
_RHS = TypeVar("_RHS")

LOCAL_NS = {
    "Json": Json,
    "ArrayVellumValueRequest": ArrayVellumValueRequest,
    "ArrayVellumValue": ArrayVellumValue,
    "ChatMessagePromptBlock": ChatMessagePromptBlock,
}


def resolve_types(value: Union[BaseDescriptor[_T], _T]) -> Tuple[Type[_T], ...]:
    if isinstance(value, BaseDescriptor):
        return value.types

    return (value.__class__,)


def resolve_combined_types(
    lhs: Union[BaseDescriptor[_LHS], _LHS], rhs: Union[BaseDescriptor[_RHS], _RHS]
) -> Tuple[Union[Type[_LHS], Type[_RHS]], ...]:
    lhs_types = resolve_types(lhs)
    rhs_types = resolve_types(rhs)

    unique_results = set(lhs_types) | set(rhs_types)

    return tuple(unique_results)


def infer_types(object_: Type, attr_name: str, localns: Optional[Dict[str, Any]] = None) -> Tuple[Type, ...]:
    try:
        class_ = object_
        type_var_mapping = {}
        if isinstance(object_, UnderGenericAlias):
            origin = get_origin(object_)
            if origin and Generic in origin.__bases__:
                class_ = origin
                args = get_args(object_)
                type_var_mapping = {t: a for t, a in zip(origin.__parameters__, args)}

        type_hints = get_type_hints(class_, localns=LOCAL_NS if localns is None else {**LOCAL_NS, **localns})
        if attr_name in type_hints:
            type_hint = type_hints[attr_name]
            if get_origin(type_hint) is ClassVar:
                return get_args(type_hint)
            if isinstance(type_hint, type):
                return (type_hint,)
            if isinstance(type_hint, UnionGenericAlias):
                if get_origin(type_hint) is Union:
                    return get_args(type_hint)
            if isinstance(type_hint, UnderGenericAlias):
                return (type_hint,)
            if isinstance(type_hint, SpecialGenericAlias):
                return (type_hint,)
            if isinstance(type_hint, GenericAlias):
                # In future versions of python, list[str] will be a `GenericAlias`
                return (cast(Type, type_hint),)
            if isinstance(type_hint, TypeVar):
                if type_hint in type_var_mapping:
                    return (type_var_mapping[type_hint],)
                return type_hint.__constraints__
            if type_hint is Any:
                return cast(Tuple[Type[Any], ...], (Any,))

        for base in reversed(class_.__mro__):
            class_attributes = vars(base)
            if attr_name in class_attributes:
                class_attribute = class_attributes[attr_name]
                return resolve_types(class_attribute)

        raise AttributeError(f"Failed to infer type from attribute {attr_name} on {object_.__name__}")
    except TypeError:
        raise AttributeError(
            f"Found 3.9+ typing syntax for field '{attr_name}' on class '{object_.__name__}' – {object_.__annotations__[attr_name]}. Type annotations must be compatible with python version 3.8. "  # noqa: E501
        )


def get_class_attr_names(cls: Type) -> Set[str]:
    # gets type-annotated attributes `foo: int`
    type_annotated_attributes: Set[str] = set()

    # gets attributes declared `foo = 1`
    class_attributes: Set[str] = set()

    for base in reversed(cls.__mro__):
        ann = base.__dict__.get("__annotations__", {})
        type_annotated_attributes.update(ann.keys())

        base_vars = vars(base).keys()
        class_attributes.update(base_vars)

    # combine and filter out private attributes
    return {a for a in list(set(class_attributes) | set(type_annotated_attributes)) if not a.startswith("_")}


def deepcopy_with_exclusions(
    obj: _T,
    memo: Any,
    exclusions: Optional[Dict[str, Any]] = None,
) -> _T:
    cls = obj.__class__
    new_instance = cls.__new__(cls)
    new_instance.__dict__.update(obj.__dict__)

    exclusions = exclusions or {}

    for key, value in obj.__dict__.items():
        if key in exclusions:
            continue
        new_instance.__dict__[key] = deepcopy(value, memo)

    for key, value in exclusions.items():
        new_instance.__dict__[key] = value

    return new_instance


def get_class_by_qualname(qualname: str) -> Type:
    module_name, class_name = qualname.rsplit(".", 1)
    module = importlib.import_module(module_name)
    imported_class = getattr(module, class_name)
    if not isinstance(imported_class, type):
        raise ValueError(f"Class {qualname} is not a valid type")

    return imported_class


def datetime_now() -> datetime:
    """
    There's a race condition between freezegun and pydantic that causes `PydanticSchemaGenerationError`
    because freezegun monkey-patches `datetime.now` to return a frozen datetime. This helper provides
    an alternative way to facilitate testing that doesn't rely on freezegun.
    """

    return datetime.now()


def get_original_base(cls: Type) -> Type:
    if not hasattr(cls, "__orig_bases__"):
        return type(None)

    # in Python 3.12, there is `from types import get_original_bases`, making this future proof
    # https://docs.python.org/3/library/types.html#types.get_original_bases
    return cls.__orig_bases__[0]  # type: ignore[attr-defined]
