from dataclasses import asdict, is_dataclass
from datetime import datetime
import enum
import inspect
from io import StringIO
from json import JSONEncoder
from queue import Queue
import sys
from uuid import UUID
from typing import Any, Callable, Dict, Type

from pydantic import BaseModel

from vellum.workflows.constants import undefined
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState, NodeExecutionCache
from vellum.workflows.utils.functions import compile_function_definition


def virtual_open(file_path: str, mode: str = "r"):
    """
    Open a file, checking VirtualFileFinder instances first before falling back to regular open().
    """
    for finder in sys.meta_path:
        if hasattr(finder, "loader") and hasattr(finder.loader, "_get_code"):
            namespace = finder.loader.namespace
            if file_path.startswith(namespace + "/"):
                relative_path = file_path[len(namespace) + 1 :]
                content = finder.loader._get_code(relative_path)
                if content is not None:
                    return StringIO(content)

    return open(file_path, mode)


class DefaultStateEncoder(JSONEncoder):
    encoders: Dict[Type, Callable] = {}

    def default(self, obj: Any) -> Any:
        if isinstance(obj, CoalesceExpression):
            empty_state = BaseState()
            return self.default(obj.resolve(empty_state))

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

        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)

        if isinstance(obj, type):
            return str(obj)

        if callable(obj):
            function_definition = compile_function_definition(obj)
            source_path = inspect.getsourcefile(obj)
            if source_path is not None:
                with virtual_open(source_path) as f:
                    source_code = f.read()
            else:
                source_code = f"# Error: Source code not available for {obj.__name__}"

            return {
                "type": "CODE_EXECUTION",
                "name": function_definition.name,
                "description": function_definition.description,
                "definition": function_definition,
                "src": source_code,
            }

        if obj.__class__ in self.encoders:
            return self.encoders[obj.__class__](obj)

        return super().default(obj)
