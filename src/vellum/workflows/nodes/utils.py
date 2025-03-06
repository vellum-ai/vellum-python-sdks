from functools import cache
import json
import re
import sys
from types import ModuleType
from typing import Any, Callable, ForwardRef, Optional, Type, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel, ValidationError

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes import BaseNode
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.ports.port import Port
from vellum.workflows.types.core import Json
from vellum.workflows.types.generics import NodeType

ADORNMENT_MODULE_NAME = "<adornment>"


@cache
def get_unadorned_node(node: Type[BaseNode]) -> Type[BaseNode]:
    wrapped_node = get_wrapped_node(node)
    if wrapped_node is not None:
        return get_unadorned_node(wrapped_node)

    return node


@cache
def get_unadorned_port(port: Port) -> Port:
    unadorned_node = get_unadorned_node(port.node_class)
    if unadorned_node == port.node_class:
        return port

    return getattr(unadorned_node.Ports, port.name)


def get_wrapped_node(node: Type[NodeType]) -> Optional[Type[BaseNode]]:
    if not issubclass(node, BaseAdornmentNode):
        return None

    return node.__wrapped_node__


AdornableNode = TypeVar("AdornableNode", bound=BaseNode)


def create_adornment(
    adornable_cls: Type[AdornableNode], attributes: Optional[dict[str, Any]] = None
) -> Callable[..., Type["AdornableNode"]]:
    def decorator(inner_cls: Type[BaseNode]) -> Type["AdornableNode"]:
        # Investigate how to use dependency injection to avoid circular imports
        # https://app.shortcut.com/vellum/story/4116
        from vellum.workflows import BaseWorkflow

        class Subworkflow(BaseWorkflow):
            graph = inner_cls

            # mypy is wrong here, this works and is defined
            class Outputs(inner_cls.Outputs):  # type: ignore[name-defined]
                pass

        dynamic_module = f"{inner_cls.__module__}.{inner_cls.__name__}.{ADORNMENT_MODULE_NAME}"
        # This dynamic module allows calls to `type_hints` to work
        sys.modules[dynamic_module] = ModuleType(dynamic_module)

        # We use a dynamic wrapped node class to be uniquely tied to this `inner_cls` node during serialization
        WrappedNode = type(
            adornable_cls.__name__,
            (adornable_cls,),
            {
                "__wrapped_node__": inner_cls,
                "__module__": dynamic_module,
                "subworkflow": Subworkflow,
                "Ports": type("Ports", (adornable_cls.Ports,), {port.name: port.copy() for port in inner_cls.Ports}),
                **(attributes or {}),
            },
        )
        return WrappedNode

    return decorator


def parse_type_from_str(result_as_str: str, output_type: Any) -> Any:
    if output_type is str:
        return result_as_str

    if output_type is float:
        return float(result_as_str)

    if output_type is int:
        return int(result_as_str)

    if output_type is bool:
        return bool(result_as_str)

    if get_origin(output_type) is list:
        try:
            data = json.loads(result_as_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON Array format for result_as_str")

        if not isinstance(data, list):
            raise ValueError(f"Expected a list of items for result_as_str, received {data.__class__.__name__}")

        inner_type = get_args(output_type)[0]
        if issubclass(inner_type, BaseModel):
            return [inner_type.model_validate(item) for item in data]
        else:
            return data

    if output_type is Json:
        try:
            data = json.loads(result_as_str)
            # If we got a FunctionCallVellumValue, return just the value
            if isinstance(data, dict) and data.get("type") == "FUNCTION_CALL" and "value" in data:
                return data["value"]
            return data
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for result_as_str")

    if get_origin(output_type) is Union:
        for inner_type in get_args(output_type):
            try:
                return parse_type_from_str(result_as_str, inner_type)
            except ValueError:
                continue
        raise ValueError(f"Could not parse with any of the Union types: {output_type}")

    if issubclass(output_type, BaseModel):
        try:
            data = json.loads(result_as_str)
            # If we got a FunctionCallVellumValue extract FunctionCall,
            if (
                hasattr(output_type, "__name__")
                and output_type.__name__ == "FunctionCall"
                and isinstance(data, dict)
                and "value" in data
            ):
                data = data["value"]
            return output_type.model_validate(data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for result_as_str")

    raise ValueError(f"Unsupported output type: {output_type}")


def _get_type_name(obj: Any) -> str:
    if isinstance(obj, type):
        return obj.__name__

    if get_origin(obj) is Union:
        children = [_get_type_name(child) for child in get_args(obj)]
        return " | ".join(children)

    return str(obj)


def cast_to_output_type(result: Any, output_type: Any) -> Any:
    if isinstance(output_type, ForwardRef) or output_type is Any:
        # Treat ForwardRefs as Any for now
        return result

    is_valid_output_type = isinstance(output_type, type)
    if get_origin(output_type) is Union:
        allowed_types = get_args(output_type)
        for allowed_type in allowed_types:
            try:
                return cast_to_output_type(result, allowed_type)
            except NodeException:
                continue
    elif get_origin(output_type) is list:
        allowed_item_type = get_args(output_type)[0]
        if isinstance(result, list):
            return [cast_to_output_type(item, allowed_item_type) for item in result]
    elif is_valid_output_type and issubclass(output_type, BaseModel) and not isinstance(result, output_type):
        try:
            return output_type.model_validate(result)
        except ValidationError as e:
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message=re.sub(r"\s+For further information visit [^\s]+", "", str(e)),
            ) from e
    elif is_valid_output_type and isinstance(result, output_type):
        return result

    output_type_name = _get_type_name(output_type)
    result_type_name = _get_type_name(type(result))
    raise NodeException(
        code=WorkflowErrorCode.INVALID_OUTPUTS,
        message=f"Expected an output of type '{output_type_name}', but received '{result_type_name}'",
    )
