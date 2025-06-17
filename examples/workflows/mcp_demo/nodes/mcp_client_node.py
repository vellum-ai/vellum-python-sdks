import asyncio
import os
from typing import List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from vellum import FunctionDefinition
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.environment_variable import EnvironmentVariableReference


class MCPClientNode(BaseNode):

    token = EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN", default="")

    class Outputs(BaseNode.Outputs):
        tools: List[FunctionDefinition]
        thinking: str

    def run(self) -> Outputs:
        server_params = StdioServerParameters(
            command="/usr/local/bin/docker",
            args=["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": self.token,
            },
        )

        async def run_stdio():
            async with stdio_client(server_params) as stdio_transport:
                stdio_stream, write_stream = stdio_transport
                async with ClientSession(stdio_stream, write_stream) as session:
                    await session.initialize()
                    response = await session.list_tools()
            return response.tools

        mcp_tools = asyncio.run(run_stdio())

        return self.Outputs(
            tools=[
                FunctionDefinition(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.inputSchema,
                )
                for tool in mcp_tools
            ],
            thinking=f"Retrieved {len(mcp_tools)} tools from MCP Server...",
        )
