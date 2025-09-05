from typing import List

from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.prompt_block import PromptBlock
from vellum.client.types.prompt_parameters import PromptParameters
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow

from .get_current_weather import get_current_weather


class Inputs(BaseInputs):
    query: str


class GetCurrentWeatherNode(ToolCallingNode):
    """
    A tool calling node that calls the get_current_weather function.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a weather expert",
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
                            input_variable="question",
                        ),
                    ],
                ),
            ],
        ),
    ]
    functions = [get_current_weather]
    prompt_inputs = {
        "question": Inputs.query,
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0.0,
        max_tokens=4096,
        top_p=1.0,
        top_k=0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        logit_bias=None,
        custom_parameters={"mode": "initial"},
    )

    def process_parameters(self, parameters: PromptParameters) -> PromptParameters:
        """
        Override process_parameters to add custom parameter processing.
        """
        parameters = parameters.model_copy(update={"custom_parameters": {"mode": "updated"}})

        return parameters

    def process_blocks(self, blocks: List[PromptBlock]) -> List[PromptBlock]:
        """
        Override process_blocks to add custom block processing.
        """

        # Add a new block to the list
        blocks.append(
            VariablePromptBlock(
                block_type="VARIABLE", state=None, cache_config=None, input_variable="additional_blocks"
            )
        )

        return blocks


class BasicToolCallingNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    """
    A workflow that uses the GetCurrentWeatherNode.
    """

    graph = GetCurrentWeatherNode

    class Outputs(BaseWorkflow.Outputs):
        text = GetCurrentWeatherNode.Outputs.text
        chat_history = GetCurrentWeatherNode.Outputs.chat_history
