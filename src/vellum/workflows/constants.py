from enum import Enum
from typing import Any, cast


class _UndefMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> type:
        cls.__name__ = "undefined"
        cls.__qualname__ = "undefined"

        undefined_class = super().__new__(cls, name, bases, attrs)
        undefined_class.__name__ = "undefined"
        undefined_class.__qualname__ = "undefined"
        return undefined_class

    def __repr__(cls) -> str:
        return "undefined"

    def __getattribute__(cls, name: str) -> Any:
        if name == "__class__":
            # ensures that undefined.__class__ == undefined
            return cls

        return super().__getattribute__(name)

    def __bool__(cls) -> bool:
        return False


class undefined(metaclass=_UndefMeta):
    """
    A singleton class that represents an `undefined` value, mirroring the behavior of the `undefined`
    value in TypeScript.
    """

    pass


LATEST_RELEASE_TAG = "LATEST"

OMIT = cast(Any, ...)


class APIRequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    CONNECT = "CONNECT"
    TRACE = "TRACE"


class AuthorizationType(Enum):
    BEARER_TOKEN = "BEARER_TOKEN"
    API_KEY = "API_KEY"
