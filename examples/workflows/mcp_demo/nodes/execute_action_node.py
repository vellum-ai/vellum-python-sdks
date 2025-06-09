import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from vellum import ChatMessage, FunctionCallChatMessageContent, StringChatMessageContent
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.environment_variable import EnvironmentVariableReference

from ..state import State
from .my_prompt_node import MyPromptNode


class ExecuteActionNode(BaseNode[State]):
    action = MyPromptNode.Outputs.results[0]
    token = EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN", default="")

    class Outputs(BaseNode.Outputs):
        action_result: str
        thinking: str

    def run(self) -> Outputs:
        if self.action.type != "FUNCTION_CALL":
            raise ValueError(f"Action is not a function call: {self.action}")

        self.state.chat_history.append(
            ChatMessage(
                role="ASSISTANT",
                content=FunctionCallChatMessageContent.model_validate(self.action.model_dump()),
            )
        )

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
                    response = await session.call_tool(
                        name=self.action.value.name,
                        arguments=self.action.value.arguments,
                    )

            return response.content

        action_results = asyncio.run(run_stdio())
        compiled_action_result = "\n".join([res.text for res in action_results if res.type == "text"])
        self.state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=compiled_action_result),
                source=self.action.value.id,
            )
        )

        return self.Outputs(
            action_result=compiled_action_result,
            thinking=f"Executed tool: {self.action.value.name}",
        )
