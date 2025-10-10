from abc import ABC, ABCMeta
import inspect
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Iterator, Tuple, Type, cast, get_origin

if TYPE_CHECKING:
    from vellum.workflows.graph.graph import Graph, GraphTarget
    from vellum.workflows.state.base import BaseState

from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.types.utils import get_class_attr_names, infer_types
from vellum.workflows.utils.uuids import uuid4_from_hash


def _is_annotated(cls: Type, name: str) -> bool:
    annotations = getattr(cls, "__annotations__", {})
    annotation = annotations.get(name)
    if annotation is not None:
        if get_origin(annotation) is ClassVar:
            return False
        return True

    for base in cls.__bases__:
        if _is_annotated(base, name):
            return True

    return False


class BaseTriggerMeta(ABCMeta):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        cls = super().__new__(mcs, name, bases, dct)
        trigger_cls = cast(Type["BaseTrigger"], cls)

        attribute_ids: Dict[str, Any] = {}
        for base in bases:
            base_ids = getattr(base, "__trigger_attribute_ids__", None)
            if isinstance(base_ids, dict):
                attribute_ids.update(base_ids)

        annotations = getattr(trigger_cls, "__annotations__", {})
        for attr_name, annotation in annotations.items():
            if attr_name.startswith("_"):
                continue
            if attr_name in trigger_cls.__dict__:
                continue
            if get_origin(annotation) is ClassVar:
                continue
            attribute_ids[attr_name] = uuid4_from_hash(
                f"{trigger_cls.__module__}|{trigger_cls.__qualname__}|{attr_name}"
            )

        trigger_cls.__trigger_attribute_ids__ = attribute_ids
        trigger_cls.__trigger_attribute_cache__ = {}
        return trigger_cls

    """
    Metaclass for BaseTrigger that enables class-level >> operator.

    This allows triggers to be used at the class level, similar to nodes:
        ManualTrigger >> MyNode  # Class-level, no instantiation
    """

    def __getattribute__(cls, name: str) -> Any:
        trigger_cls = cast(Type["BaseTrigger"], cls)
        if name.startswith("_"):
            return super().__getattribute__(name)

        try:
            attribute = super().__getattribute__(name)
        except AttributeError as exc:
            if _is_annotated(cls, name):
                attribute = None
            else:
                raise exc

        if inspect.isroutine(attribute) or isinstance(attribute, (property, classmethod, staticmethod)):
            return attribute

        if isinstance(attribute, TriggerAttributeReference):
            return attribute

        if name in cls.__dict__:
            return attribute

        if not _is_annotated(cls, name):
            return attribute

        cache = getattr(cls, "__trigger_attribute_cache__", {})
        if name in cache:
            return cache[name]

        for base in cls.__mro__[1:]:
            base_cache = getattr(base, "__trigger_attribute_cache__", None)
            if base_cache and name in base_cache:
                cache[name] = base_cache[name]
                return base_cache[name]

        types = infer_types(cls, name)
        reference = TriggerAttributeReference(name=name, types=types, instance=attribute, trigger_class=trigger_cls)
        cache[name] = reference
        cls.__trigger_attribute_cache__ = cache
        return reference

    def __iter__(cls) -> Iterator[TriggerAttributeReference]:
        cache = getattr(cls, "__trigger_attribute_cache__", {})
        seen: Dict[str, TriggerAttributeReference] = dict(cache)

        for base in cls.__mro__[1:]:
            base_cache = getattr(base, "__trigger_attribute_cache__", None)
            if not base_cache:
                continue
            for key, value in base_cache.items():
                seen.setdefault(key, value)

        for attr_name in get_class_attr_names(cls):
            if attr_name in seen:
                yield seen[attr_name]
                continue

            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, TriggerAttributeReference):
                seen[attr_name] = attr_value
                yield attr_value

    def __rshift__(cls, other: "GraphTarget") -> "Graph":  # type: ignore[misc]
        """
        Enable Trigger class >> Node syntax (class-level only).

        Args:
            other: The target to connect to - can be a Node, Graph, or set of Nodes

        Returns:
            Graph: A graph object with trigger edges

        Examples:
            ManualTrigger >> MyNode
            ManualTrigger >> {NodeA, NodeB}
            ManualTrigger >> (NodeA >> NodeB)
        """
        from vellum.workflows.edges.trigger_edge import TriggerEdge
        from vellum.workflows.graph.graph import Graph
        from vellum.workflows.nodes.bases.base import BaseNode as BaseNodeClass

        # Cast cls to the proper type for TriggerEdge
        trigger_cls = cast(Type["BaseTrigger"], cls)

        if isinstance(other, set):
            # Trigger >> {NodeA, NodeB}
            trigger_edges = []
            graph_items = []
            for item in other:
                if isinstance(item, type) and issubclass(item, BaseNodeClass):
                    trigger_edges.append(TriggerEdge(trigger_cls, item))
                elif isinstance(item, Graph):
                    # Trigger >> {Graph1, Graph2}
                    graph_items.append(item)
                    for entrypoint in item.entrypoints:
                        trigger_edges.append(TriggerEdge(trigger_cls, entrypoint))
                else:
                    raise TypeError(
                        f"Cannot connect trigger to {type(item).__name__}. " f"Expected BaseNode or Graph in set."
                    )

            result_graph = Graph.from_trigger_edges(trigger_edges)

            for graph_item in graph_items:
                result_graph._extend_edges(graph_item.edges)
                result_graph._terminals.update(graph_item._terminals)
                for existing_trigger_edge in graph_item._trigger_edges:
                    if existing_trigger_edge not in result_graph._trigger_edges:
                        result_graph._trigger_edges.append(existing_trigger_edge)

            return result_graph

        elif isinstance(other, Graph):
            # Trigger >> Graph
            edges = [TriggerEdge(trigger_cls, entrypoint) for entrypoint in other.entrypoints]
            result_graph = Graph.from_trigger_edges(edges)
            # Also include the edges from the original graph
            result_graph._extend_edges(other.edges)
            result_graph._terminals = other._terminals
            return result_graph

        elif isinstance(other, type) and issubclass(other, BaseNodeClass):
            # Trigger >> Node
            edge = TriggerEdge(trigger_cls, other)
            return Graph.from_trigger_edge(edge)

        else:
            raise TypeError(
                f"Cannot connect trigger to {type(other).__name__}. " f"Expected BaseNode, Graph, or set of BaseNodes."
            )

    def __rrshift__(cls, other: Any) -> "Graph":
        """
        Prevent Node >> Trigger class syntax.

        Raises:
            TypeError: Always, as this operation is not allowed
        """
        raise TypeError(
            f"Cannot create edge targeting trigger {cls.__name__}. "
            f"Triggers must be at the start of a graph path, not as targets. "
            f"Did you mean: {cls.__name__} >> {other.__name__ if hasattr(other, '__name__') else other}?"
        )


class BaseTrigger(ABC, metaclass=BaseTriggerMeta):
    """
    Base class for workflow triggers - first-class graph elements.

    Triggers define how and when a workflow execution is initiated. They are integrated
    into the workflow graph using the >> operator and can connect to nodes at the class level.

    Examples:
        # Class-level usage (consistent with nodes)
        ManualTrigger >> MyNode
        ManualTrigger >> {NodeA, NodeB}
        ManualTrigger >> (NodeA >> NodeB)

    Subclass Hierarchy:
        - ManualTrigger: Explicit workflow invocation (default)
        - IntegrationTrigger: External service triggers (base for Slack, GitHub, etc.)
        - ScheduledTrigger: Time-based triggers with cron/interval schedules

    Important:
        Triggers can only appear at the start of graph paths. Attempting to create
        edges targeting triggers (Node >> Trigger) will raise a TypeError.

    Note:
        Like nodes, triggers work at the class level only. Do not instantiate triggers.
    """

    __trigger_attribute_ids__: Dict[str, Any]
    __trigger_attribute_cache__: Dict[str, "TriggerAttributeReference[Any]"]

    @classmethod
    def attribute_references(cls) -> Dict[str, "TriggerAttributeReference[Any]"]:
        """Return class-level trigger attribute descriptors keyed by attribute name."""

        return {reference.name: reference for reference in cls}

    def to_trigger_attribute_values(self) -> Dict["TriggerAttributeReference[Any]", Any]:
        """Materialize attribute descriptor/value pairs for this trigger instance."""

        attribute_values: Dict["TriggerAttributeReference[Any]", Any] = {}
        for reference in type(self):
            if hasattr(self, reference.name):
                attribute_values[reference] = getattr(self, reference.name)
            elif type(None) in reference.types:
                attribute_values[reference] = None
            else:
                raise AttributeError(
                    f"{type(self).__name__} did not populate required trigger attribute '{reference.name}'"
                )

        return attribute_values

    def bind_to_state(self, state: "BaseState") -> None:
        """Persist this trigger's attribute values onto the provided state."""

        state.meta.trigger_attributes.update(self.to_trigger_attribute_values())
