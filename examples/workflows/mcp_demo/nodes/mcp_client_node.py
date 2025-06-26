import asyncio
import os
import traceback
from typing import List

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from vellum import FunctionDefinition
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.environment_variable import EnvironmentVariableReference


class MCPClientNode(BaseNode):

    token = EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN", default="")

    class Outputs(BaseNode.Outputs):
        tools: List[FunctionDefinition]
        thinking: str

    def run(self) -> Outputs:
        async def run_stdio():
            async with streamablehttp_client(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": f"Bearer {self.token}",
                },
            ) as http_stream:
                read_stream, write_stream, get_id = http_stream
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    response = await session.list_tools()
            return response.tools

        try:
            mcp_tools = asyncio.run(run_stdio())
        except Exception as e:
            tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            raise NodeException(
                f"Error: Failed to retrieve tools from MCP Server: {tb_str}",
                code=WorkflowErrorCode.INVALID_CODE,
            )

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
