from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.mcp_server_url_env_var_node import MCPServerUrlEnvVarNode


class BasicToolCallingNodeMCPUrlEnvVarWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = MCPServerUrlEnvVarNode

    class Outputs(BaseWorkflow.Outputs):
        text = MCPServerUrlEnvVarNode.Outputs.text
        chat_history = MCPServerUrlEnvVarNode.Outputs.chat_history
