from uuid import UUID
from typing import Any, Callable, ClassVar, Generic, Optional, Type, TypeVar, cast

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME, get_wrapped_node
from vellum.workflows.types.core import JsonObject
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_TryNodeType = TypeVar("_TryNodeType", bound=TryNode)


class BaseTryNodeDisplay(BaseNodeVellumDisplay[_TryNodeType], Generic[_TryNodeType]):
    error_output_id: ClassVar[Optional[UUID]] = None

    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        node = self._node

        try:
            inner_node = get_wrapped_node(node)
        except AttributeError:
            subworkflow = raise_if_descriptor(node.subworkflow)
            if not isinstance(subworkflow.graph, type) or not issubclass(subworkflow.graph, BaseNode):
                raise NotImplementedError(
                    "Unable to serialize Try Nodes that wrap subworkflows containing more than one Node."
                )

            inner_node = subworkflow.graph

        # We need the node display class of the underlying node because
        # it contains the logic for serializing the node and potential display overrides
        node_display_class = get_node_display_class(BaseNodeVellumDisplay, inner_node)
        node_display = node_display_class()

        serialized_node = node_display.serialize(
            display_context,
            error_output_id=self.error_output_id or uuid4_from_hash(f"{node_display.node_id}|error_output_id"),
        )

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

    @classmethod
    def wrap(cls, error_output_id: Optional[UUID] = None) -> Callable[..., Type["BaseTryNodeDisplay"]]:
        _error_output_id = error_output_id

        NodeDisplayType = TypeVar("NodeDisplayType", bound=BaseNodeDisplay)

        def decorator(inner_cls: Type[NodeDisplayType]) -> Type[NodeDisplayType]:
            node_class = inner_cls.infer_node_class()
            wrapped_node_class = cast(Type[BaseNode], node_class.__wrapped_node__)

            # Mypy gets mad about dynamic parameter types like this, but it's fine
            class TryNodeDisplay(BaseTryNodeDisplay[node_class]):  # type: ignore[valid-type]
                error_output_id = _error_output_id

            setattr(inner_cls, "__adorned_by__", TryNodeDisplay)

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
