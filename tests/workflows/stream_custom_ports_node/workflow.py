from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.jinja_prompt_block import JinjaPromptBlock
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.ports.port import Port
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    should_execute: bool = True


class MyPrompt(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="Hello, world!",
                )
            ],
        )
    ]

    class Ports(InlinePromptNode.Ports):
        execute_branch = Port.on_if(Inputs.should_execute)
        skip_branch = Port.on_else()


class MyFinalOutput(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = MyPrompt.Outputs.text


class StreamCustomPortsWorkflow(BaseWorkflow):
    graph = MyPrompt.Ports.execute_branch >> MyFinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = MyFinalOutput.Outputs.value
