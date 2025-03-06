import inspect
from typing import Any, Callable, Generic, Optional, Tuple, Type, TypeVar, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.nodes.vellum.base_adornment_node import BaseAdornmentNodeDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_RetryNodeType = TypeVar("_RetryNodeType", bound=RetryNode)


class BaseRetryNodeDisplay(BaseAdornmentNodeDisplay[_RetryNodeType], Generic[_RetryNodeType]):
    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        node = self._node
        node_id = self.node_id

        attributes: JsonArray = []
        for attribute in node:
            if inspect.isclass(attribute.instance) and issubclass(attribute.instance, BaseWorkflow):
                # We don't need to serialize attributes that are workflows
                continue

            id = str(uuid4_from_hash(f"{node_id}|{attribute.name}"))
            attributes.append(
                {
                    "id": id,
                    "name": attribute.name,
                    "value": self.serialize_value(display_context, cast(BaseDescriptor, attribute.instance)),
                }
            )

        adornment: JsonObject = {
            "id": str(node_id),
            "label": node.__qualname__,
            "base": self.get_base().dict(),
            "attributes": attributes,
        }

        serialized_node = super().serialize(
            display_context,
            adornment=adornment,
        )

        if serialized_node["type"] == "GENERIC":
            return serialized_node

        serialized_node_definition = serialized_node.get("definition")
        if isinstance(serialized_node_definition, dict):
            serialized_node_definition_module = serialized_node_definition.get("module")
            if isinstance(serialized_node_definition_module, list):
                serialized_node_definition_module.extend(
                    [
                        serialized_node_definition["name"],
                        ADORNMENT_MODULE_NAME,
                    ]
                )
                serialized_node_definition["name"] = node.__name__

        return serialized_node

    def get_node_output_display(self, output: OutputReference) -> Tuple[Type[BaseNode], NodeOutputDisplay]:
        inner_node = self._node.__wrapped_node__
        if not inner_node:
            return super().get_node_output_display(output)

        node_display_class = get_node_display_class(BaseNodeDisplay, inner_node)
        node_display = node_display_class()

        inner_output = getattr(inner_node.Outputs, output.name)
        return node_display.get_node_output_display(inner_output)

    @classmethod
    def wrap(
        cls,
        max_attempts: int,
        delay: Optional[float] = None,
        retry_on_error_code: Optional[WorkflowErrorCode] = None,
        retry_on_condition: Optional[BaseDescriptor] = None,
    ) -> Callable[..., Type["BaseRetryNodeDisplay"]]:
        _max_attempts = max_attempts
        _delay = delay
        _retry_on_error_code = retry_on_error_code
        _retry_on_condition = retry_on_condition

        NodeDisplayType = TypeVar("NodeDisplayType", bound=BaseNodeDisplay)

        def decorator(inner_cls: Type[NodeDisplayType]) -> Type[NodeDisplayType]:
            node_class = inner_cls.infer_node_class()
            wrapped_node_class = cast(Type[BaseNode], node_class.__wrapped_node__)

            class RetryNodeDisplay(BaseRetryNodeDisplay[node_class]):  # type: ignore[valid-type]
                max_attempts = _max_attempts
                delay = _delay
                retry_on_error_code = _retry_on_error_code
                retry_on_condition = _retry_on_condition

            setattr(inner_cls, "__adorned_by__", RetryNodeDisplay)

            # We must edit the node display class to use __wrapped_node__ everywhere it
            # references the adorned node class, which is three places:

            # 1. The node display class' parameterized type
            original_base_node_display = get_original_base(inner_cls)
            original_base_node_display.__args__ = (wrapped_node_class,)
            inner_cls._node_display_registry[wrapped_node_class] = inner_cls

            # 2. The node display class' output displays
            old_outputs = list(inner_cls.output_display.keys())
            for old_output in old_outputs:
                new_output = getattr(wrapped_node_class.Outputs, old_output.name)
                inner_cls.output_display[new_output] = inner_cls.output_display.pop(old_output)

            # 3. The node display class' port displays
            old_ports = list(inner_cls.port_displays.keys())
            for old_port in old_ports:
                new_port = getattr(wrapped_node_class.Ports, old_port.name)
                inner_cls.port_displays[new_port] = inner_cls.port_displays.pop(old_port)

            return inner_cls

        return decorator
