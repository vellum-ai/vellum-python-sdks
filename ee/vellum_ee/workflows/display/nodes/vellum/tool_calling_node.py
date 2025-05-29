from typing import Any, Generic, TypeVar

from vellum.workflows.nodes.experimental.tool_calling_node.node import ToolCallingNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_ToolCallingNodeType = TypeVar("_ToolCallingNodeType", bound=ToolCallingNode)


class BaseToolCallingNodeDisplay(BaseNodeDisplay[_ToolCallingNodeType], Generic[_ToolCallingNodeType]):
    # Mark function_configs as unserializable since we'll merge it into functions
    __unserializable_attributes__ = {ToolCallingNode.function_configs}

    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        # Get the base serialization (this will skip function_configs due to __unserializable_attributes__)
        serialized_node = super().serialize(display_context, **kwargs)

        node = self._node
        function_configs = raise_if_descriptor(node.function_configs) or {}

        # Find and enhance the functions attribute
        functions_attr = next(attr for attr in serialized_node["attributes"] if attr["name"] == "functions")
        functions_list = functions_attr["value"]["value"]["value"]
        for function_obj in functions_list:
            if function_obj.get("type") == "CODE_EXECUTION":
                function_name = function_obj["definition"]["name"]
                config = function_configs.get(function_name, {})

                # Set runtime (from config or default)
                function_obj["runtime"] = config.get("runtime", "PYTHON_3_11_6")

                # Set packages (from config or empty list)
                packages = config.get("packages")
                function_obj["packages"] = [package.dict() for package in packages] if packages is not None else []

        return serialized_node
