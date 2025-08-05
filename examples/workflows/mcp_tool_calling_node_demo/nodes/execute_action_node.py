import asyncio

from vellum import ChatMessage, FunctionCallChatMessageContent, StringChatMessageContent
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.environment_variable import EnvironmentVariableReference

from ..state import State
from .mcp_http_client import MCPHttpClient
from .my_prompt_node import MyPromptNode


class ExecuteActionNode(BaseNode[State]):
    action = MyPromptNode.Outputs.results[0]
    token = EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN", default="")

    class Outputs(BaseNode.Outputs):
        action_result: str
        thinking: str

    def run(self) -> Outputs:
        print("Running ExecuteActionNode")
        if self.action.type != "FUNCTION_CALL":
            raise ValueError(f"Action is not a function call: {self.action}")

        if self.state.chat_history is None:
            self.state.chat_history = []

        self.state.chat_history.append(
            ChatMessage(
                role="ASSISTANT",
                content=FunctionCallChatMessageContent.model_validate(self.action.model_dump()),
            )
        )

        async def run_mcp_http_client():
            try:
                async with MCPHttpClient(
                    server_url="https://api.githubcopilot.com/mcp/",
                    token=self.token,
                ) as http_stream:
                    await http_stream.initialize()
                    response = await http_stream.call_tool(
                        name=self.action.value.name,
                        arguments=self.action.value.arguments,
                    )

                return response.get("result", {}).get("content", "")
            except Exception as e:
                return str(e)

        action_results = asyncio.run(run_mcp_http_client())
        if isinstance(action_results, str):
            compiled_action_result = action_results
        else:
            compiled_action_result = "\n".join([res["text"] for res in action_results if res["type"] == "text"])

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
