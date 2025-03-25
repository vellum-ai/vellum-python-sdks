from functools import cache
import json
import sys
from types import ModuleType
from typing import Any, Callable, Dict, ForwardRef, List, Optional, Type, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel, create_model

from vellum.client.types.function_call import FunctionCall
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
        # Handle empty string case for list types by returning an empty list
        if not result_as_str.strip():
            return []

        try:
            data = json.loads(result_as_str)
        except json.JSONDecodeError:
            # raise ValueError("Invalid JSON Array format for result_as_str")
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message="Invalid JSON Array format for result_as_str",
            )

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
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message="Invalid JSON format for result_as_str",
            )

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
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message="Invalid JSON format for result_as_str",
            )

    raise ValueError(f"Unsupported output type: {output_type}")


def _get_type_name(obj: Any) -> str:
    if isinstance(obj, type):
        return obj.__name__

    if get_origin(obj) is Union:
        children = [_get_type_name(child) for child in get_args(obj)]
        return " | ".join(children)

    return str(obj)


def _clean_output_type(output_type: Any) -> Any:
    """
    pydantic currently has a bug where it doesn't support forward references in the create_model function. It will
    fail due to a max recursion depth error. This negatively impacts our `Json` type, but could also apply to other
    user defined ForwardRef types.
    """
    if get_origin(output_type) is Union:
        clean_args = [_clean_output_type(child) for child in get_args(output_type)]
        return Union[tuple(clean_args)]

    if isinstance(output_type, ForwardRef):
        # Here is where we prevent the max recursion depth error
        return Any

    if get_origin(output_type) is list:
        clean_args = [_clean_output_type(child) for child in get_args(output_type)]
        return List[clean_args[0]]  # type: ignore[valid-type]

    if get_origin(output_type) is dict:
        clean_args = [_clean_output_type(child) for child in get_args(output_type)]
        return Dict[clean_args[0], clean_args[1]]  # type: ignore[valid-type]

    return output_type


def _get_default_value(output_type: Any) -> Any:
    origin = get_origin(output_type)
    args = get_args(output_type)

    if output_type is int or output_type is float:
        return 0.0
    elif output_type is str:
        return ""
    elif origin is list:
        return []
    elif output_type is FunctionCall:
        return {}
    elif origin is Union:
        # Always use the first argument type's default value
        if args:
            return _get_default_value(args[0])
        return None
    else:
        # We defined Json as Any now which is why it returns None
        return None


def cast_to_output_type(result: Any, output_type: Any) -> Any:
    if result is None:
        return _get_default_value(output_type)

    clean_output_type = _clean_output_type(output_type)
    DynamicModel = create_model("Output", output_type=(clean_output_type, ...))

    try:
        # mypy doesn't realize that this dynamic model has the output_type field defined above
        return DynamicModel.model_validate({"output_type": result}).output_type  # type: ignore[attr-defined]
    except Exception:
        output_type_name = _get_type_name(output_type)
        result_type_name = _get_type_name(type(result))
        raise NodeException(
            code=WorkflowErrorCode.INVALID_OUTPUTS,
            message=f"Expected an output of type '{output_type_name}', but received '{result_type_name}'",
        )
