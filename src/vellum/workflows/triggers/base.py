from abc import ABC, ABCMeta
from typing import TYPE_CHECKING, Any, Type, cast

if TYPE_CHECKING:
    from vellum.workflows.graph.graph import Graph, GraphTarget


class BaseTriggerMeta(ABCMeta):
    """
    Metaclass for BaseTrigger that enables class-level >> operator.

    This allows triggers to be used at the class level, similar to nodes:
        ManualTrigger >> MyNode  # Class-level, no instantiation
    """

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
        trigger_cls = cast("Type[BaseTrigger]", cls)

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

    pass
