from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from vellum.workflows.nodes.bases import BaseNode
    from vellum.workflows.triggers.base import BaseTrigger


class TriggerEdge:
    """
    Represents an edge from a Trigger to a Node in the workflow graph.

    TriggerEdge is analogous to Edge, but connects triggers to nodes instead of
    nodes to nodes. These edges define which nodes should be executed when a
    particular trigger fires.

    Examples:
        ManualTrigger >> MyNode  # Creates TriggerEdge(ManualTrigger, MyNode)
        SlackTrigger >> ProcessNode  # Creates TriggerEdge(SlackTrigger, ProcessNode)

    Attributes:
        trigger_class: The trigger class that initiates execution
        to_node: The node that should execute when the trigger fires
    """

    def __init__(self, trigger_class: Type["BaseTrigger"], to_node: Type["BaseNode"]):
        """
        Initialize a TriggerEdge.

        Args:
            trigger_class: The trigger class that initiates execution
            to_node: The node class that should execute when triggered
        """
        self.trigger_class = trigger_class
        self.to_node = to_node

    def __eq__(self, other: Any) -> bool:
        """
        Two TriggerEdges are equal if they have the same trigger and target node.

        Args:
            other: Another object to compare with

        Returns:
            True if both edges connect the same trigger to the same node
        """
        if not isinstance(other, TriggerEdge):
            return False

        return self.trigger_class == other.trigger_class and self.to_node == other.to_node

    def __hash__(self) -> int:
        """
        Hash based on trigger and target node for set/dict operations.

        Returns:
            Hash value for this edge
        """
        return hash((self.trigger_class, self.to_node))

    def __repr__(self) -> str:
        """
        String representation showing the trigger-to-node connection.

        Returns:
            String in format "TriggerName >> NodeName"
        """
        return f"{self.trigger_class.__name__} >> {self.to_node.__name__}"
