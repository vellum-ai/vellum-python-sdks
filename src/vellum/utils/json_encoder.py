from dataclasses import asdict, is_dataclass
from datetime import datetime
import enum
from json import JSONEncoder
from queue import Queue
from uuid import UUID
from typing import Any, Callable, Dict, Protocol, Type

from pydantic import BaseModel


class VellumJsonEncodable(Protocol):
    """Protocol for objects that can be encoded to JSON by VellumJsonEncoder.

    Classes implementing this protocol must define a __vellum_encode__ method
    that returns a JSON-serializable representation of the object.
    """

    def __vellum_encode__(self) -> Any:
        """Return a JSON-serializable representation of this object."""
        ...


class VellumJsonEncoder(JSONEncoder):
    """JSON encoder that handles Vellum-specific types.

    This encoder supports:
    - Objects implementing VellumJsonEncodable protocol
    - Pydantic BaseModel instances
    - UUIDs, sets, datetimes, enums
    - Dataclasses and Queue objects
    - Custom encoder registry via encoders dict
    """

    encoders: Dict[Type, Callable] = {}

    def default(self, obj: Any) -> Any:
        if hasattr(obj, "__vellum_encode__") and callable(getattr(obj, "__vellum_encode__")):
            return obj.__vellum_encode__()

        if isinstance(obj, UUID):
            return str(obj)

        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, BaseModel):
            return obj.model_dump()

        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, enum.Enum):
            return obj.value

        if isinstance(obj, Queue):
            return list(obj.queue)

        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)

        if isinstance(obj, type):
            return str(obj)

        if isinstance(obj, Exception):
            return str(obj)

        if obj.__class__ in self.encoders:
            return self.encoders[obj.__class__](obj)

        return super().default(obj)
