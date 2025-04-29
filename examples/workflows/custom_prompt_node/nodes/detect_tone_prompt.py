from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, RichTextPromptBlock, VariablePromptBlock
from vellum.workflows.ports import Port
from vellum.workflows.references import LazyReference

from ..inputs import Inputs
from .local_bedrock_node import LocalBedrockNode


class DetectTonePrompt(LocalBedrockNode):
    ml_model = "aws-bedrock//anthropic/claude-3-5-sonnet-20240620-v1:0/us-west-2"

    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You will be given a message and you need to detect the tone of the message.

The tone can be one of the following:
- happy
- sad
- angry


Only respond with one of those three tones and nothing more.
"""
                        )
                    ]
                )
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        VariablePromptBlock(input_variable="message"),
                    ]
                )
            ],
        ),
    ]

    prompt_inputs = {
        "message": Inputs.message,
    }

    class Ports(LocalBedrockNode.Ports):
        happy = Port.on_if(LazyReference(lambda: DetectTonePrompt.Outputs.text.equals("happy")))
        sad = Port.on_elif(LazyReference(lambda: DetectTonePrompt.Outputs.text.equals("sad")))
        angry = Port.on_elif(LazyReference(lambda: DetectTonePrompt.Outputs.text.equals("angry")))
