from typing import List

from vellum import ChatMessage
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.displayable.set_state_node import SetStateNode
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow


class State(BaseState):
    chat_history: List[ChatMessage] = []
    counter: int = 0


class Inputs(BaseInputs):
    message: str


class AgentNode(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant",
                        ),
                    ],
                ),
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        VariablePromptBlock(
                            input_variable="user_message",
                        ),
                    ],
                ),
            ],
        ),
    ]
    prompt_inputs = {
        "user_message": Inputs.message,
    }


class UpdateStateNode(SetStateNode[State]):
    operations = {
        "chat_history": State.chat_history.concat(AgentNode.Outputs.chat_history),
        "counter": State.counter + 1,
    }


class BasicSetStateNodeWorkflow(BaseWorkflow[Inputs, State]):
    graph = AgentNode >> UpdateStateNode

    class Outputs(BaseWorkflow.Outputs):
        chat_history = State.chat_history
        counter = State.counter
