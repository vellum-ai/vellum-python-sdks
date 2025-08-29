from vellum.workflows import BaseWorkflow
from vellum.workflows.state.base import BaseState

from .inputs import Inputs
from .nodes.agent_node import Agent


class MCPToolboxWorkflow(BaseWorkflow[Inputs, BaseState]):
    """
    An example workflow that uses the built-in ToolCallingNode with MCP Server.
    It interacts with the Github MCP Server to manage the user's GitHub account.

    To run this demo:
    - Create a Github Access Token and export it as the environment variable `GITHUB_PERSONAL_ACCESS_TOKEN`
    - Run this workflow: `python -m examples.workflows.mcp_tool_calling_node_demo.chat`
    """

    graph = Agent

    class Outputs:
        text = Agent.Outputs.text
        chat_history = Agent.Outputs.chat_history
