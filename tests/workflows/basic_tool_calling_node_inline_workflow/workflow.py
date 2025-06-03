from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlineSubworkflowNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.experimental.tool_calling_node import ToolCallingNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    city: str
    date: str


class NestedInputs(BaseInputs):
    metro: str


class StartNode(BaseNode):
    metro = NestedInputs.metro
    date = Inputs.date

    class Outputs(BaseOutputs):
        temperature: float
        reasoning: str

    def run(self) -> Outputs:
        return self.Outputs(temperature=70, reasoning=f"The weather in {self.metro} on {self.date} was hot")


class NestedWorkflow(BaseWorkflow[NestedInputs, BaseState]):
    graph = StartNode

    class Outputs(BaseOutputs):
        temperature = StartNode.Outputs.temperature
        reasoning = StartNode.Outputs.reasoning


class ExampleInlineSubworkflowNode(InlineSubworkflowNode):
    subworkflow_inputs = {
        "metro": Inputs.city,
    }
    subworkflow = NestedWorkflow


class BasicInlineSubworkflowWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ExampleInlineSubworkflowNode

    class Outputs(BaseOutputs):
        temperature = ExampleInlineSubworkflowNode.Outputs.temperature
        reasoning = ExampleInlineSubworkflowNode.Outputs.reasoning


class WorkflowInputs(BaseInputs):
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
    functions = [BasicInlineSubworkflowWorkflow]
    prompt_inputs = {
        "question": WorkflowInputs.query,
    }


class BasicToolCallingNodeInlineWorkflowWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    """
    A workflow that uses the GetCurrentWeatherNode.
    """

    graph = GetCurrentWeatherNode

    class Outputs(BaseWorkflow.Outputs):
        text = GetCurrentWeatherNode.Outputs.text
        chat_history = GetCurrentWeatherNode.Outputs.chat_history
