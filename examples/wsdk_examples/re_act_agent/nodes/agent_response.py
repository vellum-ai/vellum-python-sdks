from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .agent_node import AgentNode


class AgentResponse(FinalOutputNode[BaseState, str]):
    """Here we send the final response back to the user after the Agent finishes calling tools."""

    class Outputs(FinalOutputNode.Outputs):
        value = AgentNode.Outputs.text
