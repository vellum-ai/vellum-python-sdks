from dataclasses import asdict, is_dataclass
from datetime import datetime
import enum
import inspect
from json import JSONEncoder
from queue import Queue
from uuid import UUID
from typing import Any, Callable, Dict, Type

from pydantic import BaseModel

from vellum.workflows.constants import undefined
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState, NodeExecutionCache
from vellum.workflows.utils.functions import compile_function_definition


class DefaultStateEncoder(JSONEncoder):
    encoders: Dict[Type, Callable] = {}

    def default(self, obj: Any) -> Any:
        if isinstance(obj, BaseState):
            return dict(obj)

        if isinstance(obj, (BaseInputs, BaseOutputs)):
            return {descriptor.name: value for descriptor, value in obj if value is not undefined}

        if isinstance(obj, (BaseOutput, Port)):
            return obj.serialize()

        if isinstance(obj, NodeExecutionCache):
            return obj.dump()

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

        if is_dataclass(obj):
            # Technically, obj is DataclassInstance | type[DataclassInstance], but asdict expects a DataclassInstance
            # in practice, we only ever pass the former
            return asdict(obj)  # type: ignore[call-overload]

        if isinstance(obj, type):
            return str(obj)

        if callable(obj):
            function_definition = compile_function_definition(obj)
            try:
                source_code = inspect.getsource(obj)
            except Exception:
                source_code = f"<source code not available for {obj.__name__}>"

            return {
                "type": "CODE_EXECUTION",
                "definition": function_definition,
                "src": source_code,
            }

        if obj.__class__ in self.encoders:
            return self.encoders[obj.__class__](obj)

        return super().default(obj)
