from abc import ABC, ABCMeta
from uuid import UUID
from typing import TYPE_CHECKING, Any, Dict

from vellum.workflows.utils.uuids import uuid4_from_hash

if TYPE_CHECKING:
    from vellum.workflows.graph.graph import Graph, GraphTarget


class BaseTriggerMeta(ABCMeta):
    """
    Metaclass for BaseTrigger that enables class-level >> operator.

    This allows triggers to be used without instantiation, similar to nodes:
        ManualTrigger >> MyNode  # Class-level, creates default instance
        SlackTrigger(channel="alerts") >> MyNode  # Instance-level, uses configured instance
    """

    def __rshift__(cls, other: "GraphTarget") -> "Graph":
        """
        Enable Trigger class >> Node syntax (without instantiation).

        Creates a default instance of the trigger and delegates to instance __rshift__.

        Args:
            other: The target to connect to - can be a Node, Graph, or set of Nodes

        Returns:
            Graph: A graph object with trigger edges

        Examples:
            ManualTrigger >> MyNode
            ManualTrigger >> {NodeA, NodeB}
            ManualTrigger >> (NodeA >> NodeB)
        """
        # Create a default instance and use its __rshift__
        instance = cls()
        return instance >> other

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
    into the workflow graph using the >> operator and can connect to nodes.

    Examples:
        # Class-level usage (no instantiation needed for simple triggers)
        ManualTrigger >> MyNode

        # Instance-level usage (for configured triggers)
        ScheduledTrigger(cron="0 * * * *") >> MyNode
        SlackTrigger(channel="alerts") >> MyNode

    Subclass Hierarchy:
        - ManualTrigger: Explicit workflow invocation (default)
        - IntegrationTrigger: External service triggers (base for Slack, GitHub, etc.)
        - ScheduledTrigger: Time-based triggers with cron/interval schedules

    Important:
        Triggers can only appear at the start of graph paths. Attempting to create
        edges targeting triggers (Node >> Trigger) will raise a TypeError.
    """

    def __init__(self) -> None:
        self.__id__: UUID = uuid4_from_hash(f"{self.__class__.__qualname__}")

    def __rshift__(self, other: "GraphTarget") -> "Graph":
        """
        Enable Trigger >> Node/Graph/{Nodes} syntax.

        This allows triggers to be connected to nodes or groups of nodes in the workflow graph.

        Args:
            other: The target to connect to - can be a Node, Graph, or set of Nodes

        Returns:
            Graph: A graph object with trigger edges connecting this trigger to the target(s)

        Examples:
            ManualTrigger() >> MyNode
            ManualTrigger() >> {NodeA, NodeB}
            ManualTrigger() >> (NodeA >> NodeB)
        """
        from vellum.workflows.edges.trigger_edge import TriggerEdge
        from vellum.workflows.graph.graph import Graph
        from vellum.workflows.nodes.bases.base import BaseNode as BaseNodeClass

        if isinstance(other, set):
            # Trigger >> {NodeA, NodeB}
            trigger_edges = []
            graph_items = []
            for item in other:
                if isinstance(item, type) and issubclass(item, BaseNodeClass):
                    trigger_edges.append(TriggerEdge(self, item))
                elif isinstance(item, Graph):
                    # Trigger >> {Graph1, Graph2}
                    graph_items.append(item)
                    for entrypoint in item.entrypoints:
                        trigger_edges.append(TriggerEdge(self, entrypoint))
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
            edges = [TriggerEdge(self, entrypoint) for entrypoint in other.entrypoints]
            result_graph = Graph.from_trigger_edges(edges)
            # Also include the edges from the original graph
            result_graph._extend_edges(other.edges)
            result_graph._terminals = other._terminals
            return result_graph

        elif isinstance(other, type) and issubclass(other, BaseNodeClass):
            # Trigger >> Node
            edge = TriggerEdge(self, other)
            return Graph.from_trigger_edge(edge)

        else:
            raise TypeError(
                f"Cannot connect trigger to {type(other).__name__}. " f"Expected BaseNode, Graph, or set of BaseNodes."
            )

    def __rrshift__(self, other: Any) -> "Graph":
        """
        Prevent Node >> Trigger syntax.

        Triggers must always be at the start of a graph path, never as targets.
        This method raises a TypeError to catch invalid usage.

        Raises:
            TypeError: Always, as this operation is not allowed
        """
        raise TypeError(
            f"Cannot create edge targeting trigger {self.__class__.__name__}. "
            f"Triggers must be at the start of a graph path, not as targets. "
            f"Did you mean: {self.__class__.__name__}() >> {other.__name__ if hasattr(other, '__name__') else other}?"
        )

    def __hash__(self) -> int:
        """Hash based on trigger class for set/dict operations."""
        return hash(self.__class__)

    def __eq__(self, other: object) -> bool:
        """Triggers are equal if they're the same class."""
        if not isinstance(other, BaseTrigger):
            return False
        return self.__class__ == other.__class__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def get_trigger_inputs(self) -> Dict[str, Any]:
        """
        Get the inputs provided by this trigger when it fires.

        This method should be overridden by subclasses that provide trigger-specific
        data (e.g., IntegrationTrigger provides webhook payload data).

        Returns:
            Dict mapping input names to values

        Notes:
            - ManualTrigger returns empty dict (no trigger-provided inputs)
            - IntegrationTrigger subclasses return parsed payload data
            - ScheduledTrigger might return timestamp/schedule metadata
        """
        return {}

    @property
    def trigger_type(self) -> str:
        """
        Get the type identifier for this trigger.

        Used for serialization and display purposes.

        Returns:
            String identifier for this trigger type
        """
        return self.__class__.__name__.replace("Trigger", "").upper()
