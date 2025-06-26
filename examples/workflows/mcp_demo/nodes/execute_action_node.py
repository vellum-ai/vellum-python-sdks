import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from vellum import ChatMessage, FunctionCallChatMessageContent, StringChatMessageContent
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
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

        async def run_stdio():
            try:
                async with streamablehttp_client(
                    url="https://api.githubcopilot.com/mcp",
                    headers={
                        "Authorization": f"Bearer {self.token}",
                    },
                ) as http_stream:
                    read_stream, write_stream, get_id = http_stream
                    try:
                        async with ClientSession(read_stream, write_stream) as session:
                            try:
                                await session.initialize()
                                response = await session.call_tool(
                                    name=self.action.value.name,
                                    arguments=self.action.value.arguments,
                                )
                            except Exception as e:
                                return str(e)
                    except Exception as e:
                        return str(e)

                return response.content
            except Exception as e:
                return str(e)

        action_results = asyncio.run(run_stdio())
        if isinstance(action_results, str):
            compiled_action_result = action_results
        else:
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
