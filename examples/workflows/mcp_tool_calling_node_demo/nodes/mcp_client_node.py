import asyncio
import traceback
from typing import List

from vellum import FunctionDefinition
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.environment_variable import EnvironmentVariableReference

from .mcp_http_client import MCPHttpClient


class MCPClientNode(BaseNode):

    token = EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN", default="")

    class Outputs(BaseNode.Outputs):
        tools: List[FunctionDefinition]
        thinking: str

    def run(self) -> Outputs:
        print("Running MCP Client Node")

        async def run_streamable_http():
            async with MCPHttpClient(
                server_url="https://api.githubcopilot.com/mcp/",
                token=self.token,
            ) as http_stream:
                await http_stream.initialize()
                response = await http_stream.list_tools()
            return response.get("result", {}).get("tools", [])

        try:
            mcp_tools = asyncio.run(run_streamable_http())
        except Exception as e:
            tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            raise NodeException(
                f"Error: Failed to retrieve tools from MCP Server: {tb_str}",
                code=WorkflowErrorCode.INVALID_CODE,
            )

        return self.Outputs(
            tools=[
                FunctionDefinition(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["inputSchema"],
                )
                for tool in mcp_tools
            ],
            thinking=f"Retrieved {len(mcp_tools)} tools from MCP Server...",
        )
