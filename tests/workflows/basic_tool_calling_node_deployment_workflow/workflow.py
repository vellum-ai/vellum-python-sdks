from typing import List

from vellum import ChatMessage
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.experimental.tool_calling_node import ToolCallingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.definition import DeploymentDefinition

workflow_deployment_tool = DeploymentDefinition(
    deployment="deployment_1",
    release_tag="LATEST",
)


class Inputs(BaseInputs):
    query: str


class MyToolCallingNode(ToolCallingNode):
    ml_model = "gpt-4"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant. Use the available tools to help the user.",
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
                            input_variable="query",
                        ),
                    ],
                ),
            ],
        ),
    ]
    functions = [workflow_deployment_tool]
    prompt_inputs = {
        "query": Inputs.query,
    }


class BasicToolCallingNodeDeploymentWorkflowWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = MyToolCallingNode

    class Outputs(BaseWorkflow.Outputs):
        text: str = MyToolCallingNode.Outputs.text
        chat_history: List[ChatMessage] = MyToolCallingNode.Outputs.chat_history
