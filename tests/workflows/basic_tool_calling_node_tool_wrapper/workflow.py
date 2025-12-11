from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.prompt_parameters import PromptParameters
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.utils.functions import tool
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow

from .get_current_weather import get_current_weather as base_get_current_weather


class Inputs(BaseInputs):
    date_input: str


get_current_weather = tool(
    inputs={"date_input": Inputs.date_input},
    examples=[
        {"location": "San Francisco"},
        {"location": "New York", "units": "celsius"},
    ],
)(base_get_current_weather)


class GetCurrentWeatherNode(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(text="You are a weather expert"),
                    ]
                )
            ],
        ),
    ]
    functions = [get_current_weather]

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


class BasicToolCallingNodeWrapperWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = GetCurrentWeatherNode

    class Outputs(BaseWorkflow.Outputs):
        text = GetCurrentWeatherNode.Outputs.text
        chat_history = GetCurrentWeatherNode.Outputs.chat_history
