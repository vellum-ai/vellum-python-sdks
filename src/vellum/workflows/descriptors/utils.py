from collections.abc import Mapping
import dataclasses
import inspect
from typing import Any, Dict, Optional, Sequence, Set, TypeVar, Union, cast, overload

from pydantic import BaseModel

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


@overload
def resolve_value(
    value: BaseDescriptor[_T], state: BaseState, path: str = "", memo: Optional[Dict[str, Any]] = None
) -> _T: ...


@overload
def resolve_value(value: _T, state: BaseState, path: str = "", memo: Optional[Dict[str, Any]] = None) -> _T: ...


def resolve_value(
    value: Union[BaseDescriptor[_T], _T], state: BaseState, path: str = "", memo: Optional[Dict[str, Any]] = None
) -> _T:
    """
    Recursively resolves Descriptor's until we have a constant value, using BaseState.

    The nonideal casts in this method are due to the `isinstance` calls detaching types
    from the `_T` generic.
    """

    if inspect.isclass(value):
        return cast(_T, value)

    if isinstance(value, BaseDescriptor):
        resolved_value = value.resolve(state)
        if memo is not None:
            memo[path] = resolved_value
        return resolved_value

    if isinstance(value, property) or callable(value):
        return cast(_T, value)

    if isinstance(value, (str, bytes)):
        return cast(_T, value)

    if dataclasses.is_dataclass(value):
        # The `inspect.isclass` check above prevents `value` from being a class.
        dataclass_value = dataclasses.replace(  # type: ignore[type-var]
            value,
            **{
                field.name: resolve_value(getattr(value, field.name), state, path=f"{path}.{field.name}", memo=memo)
                for field in dataclasses.fields(value)
            },
        )
        return cast(_T, dataclass_value)

    if isinstance(value, BaseModel):
        pydantic_value = value.model_copy(
            update={
                key: resolve_value(getattr(value, key), state, path=f"{path}.{key}", memo=memo)
                for key in value.dict().keys()
            }
        )
        return cast(_T, pydantic_value)

    if isinstance(value, Mapping):
        mapped_value = type(value)(  # type: ignore[call-arg]
            {
                dict_key: resolve_value(dict_value, state, path=f"{path}.{dict_key}", memo=memo)
                for dict_key, dict_value in value.items()
            }
        )
        return cast(_T, mapped_value)

    if isinstance(value, Sequence):
        sequence_value = type(value)(
            resolve_value(seq_value, state, path=f"{path}.{index}", memo=memo) for index, seq_value in enumerate(value)
        )  # type: ignore[call-arg]
        return cast(_T, sequence_value)

    if isinstance(value, Set):
        set_value = type(value)(
            resolve_value(set_value, state, path=f"{path}.{index}", memo=memo) for index, set_value in enumerate(value)
        )
        return cast(_T, set_value)

    return value


def is_unresolved(value: Any) -> bool:
    """
    Recursively checks if a value has an unresolved value, represented by undefined.
    """

    if value is undefined:
        return True

    if dataclasses.is_dataclass(value):
        return any(is_unresolved(getattr(value, field.name)) for field in dataclasses.fields(value))

    if isinstance(value, BaseModel):
        return any(is_unresolved(getattr(value, key)) for key in value.model_fields.keys())

    if isinstance(value, Mapping):
        return any(is_unresolved(item) for item in value.values())

    if isinstance(value, Sequence) and not isinstance(value, str):
        return any(is_unresolved(item) for item in value)

    if isinstance(value, Set):
        return any(is_unresolved(item) for item in value)

    return False
