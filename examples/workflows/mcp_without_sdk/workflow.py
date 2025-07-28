from vellum.workflows import BaseWorkflow

from .inputs import Inputs
from .nodes.execute_action_node import ExecuteActionNode
from .nodes.exit_node import ExitNode
from .nodes.mcp_client_node import MCPClientNode
from .nodes.my_prompt_node import MyPromptNode
from .state import State


class MCPDemoWorkflow(BaseWorkflow[Inputs, State]):
    """
    An example workflow that acts as an MCP Client. It's currently hardcoded to interact with the
    Github MCP Server, found here: https://github.com/github/github-mcp-server. To run this demo,
    - Create a Github Access Token and export it as the environment variable `GITHUB_PERSONAL_ACCESS_TOKEN`
    - Run this workflow: `python -m examples.mcp_without_sdk.chat`
    """

    graph = MCPClientNode >> {
        MyPromptNode.Ports.action >> ExecuteActionNode >> MCPClientNode,
        MyPromptNode.Ports.exit >> ExitNode,
    }

    class Outputs:
        answer = ExitNode.Outputs.value
