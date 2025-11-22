import uuid
from typing import Any, Literal, Union, overload
from typing_extensions import TypeGuard


@overload
def is_valid_uuid(val: None) -> Literal[False]: ...


@overload
def is_valid_uuid(val: str) -> TypeGuard[str]: ...


@overload
def is_valid_uuid(val: uuid.UUID) -> TypeGuard[uuid.UUID]: ...


@overload
def is_valid_uuid(val: Any) -> Literal[False]: ...


def is_valid_uuid(val: Any) -> TypeGuard[Union[str, uuid.UUID]]:
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError):
        return False
