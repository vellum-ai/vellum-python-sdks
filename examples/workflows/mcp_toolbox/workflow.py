from vellum.workflows import BaseWorkflow
from vellum.workflows.state.base import BaseState

from .inputs import Inputs
from .nodes.agent_node import Agent


class MCPToolboxWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = Agent

    class Outputs:
        text = Agent.Outputs.text
        chat_history = Agent.Outputs.chat_history
