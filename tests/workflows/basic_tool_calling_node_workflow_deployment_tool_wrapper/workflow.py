from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.definition import DeploymentDefinition
from vellum.workflows.utils.functions import tool


class WorkflowInputs(BaseInputs):
    query: str
    context: str


workflow_deployment_tool = tool(
    inputs={"context": WorkflowInputs.context},
    examples=[{"city": "San Francisco", "date": "2025-01-01"}],
)(
    DeploymentDefinition(
        deployment="weather-workflow-deployment",
        release_tag="LATEST",
    )
)


class GetCurrentWeatherNode(ToolCallingNode):
    """
    A tool calling node that calls a workflow deployment with tool wrapper.
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
    functions = [workflow_deployment_tool]
    prompt_inputs = {
        "question": WorkflowInputs.query,
    }


class BasicToolCallingNodeWorkflowDeploymentToolWrapperWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    """
    A workflow that uses the GetCurrentWeatherNode with workflow deployment tool wrapper.
    """

    graph = GetCurrentWeatherNode

    class Outputs(BaseWorkflow.Outputs):
        text = GetCurrentWeatherNode.Outputs.text
        chat_history = GetCurrentWeatherNode.Outputs.chat_history
