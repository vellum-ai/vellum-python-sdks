from vellum.prompts.blocks import TextUserMessage
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.workflows.base import BaseWorkflow


class FirstToolCallingNode(ToolCallingNode):
    """
    First tool calling node with no tools defined.
    """

    ml_model = "gpt-5"
    blocks = [
        TextUserMessage(
            "You are a helpful assistant. This is the first node. Please respond with 'First node response'"
        ),
    ]
    functions = []
    prompt_inputs = {}


class SecondToolCallingNode(ToolCallingNode):
    """
    Second tool calling node with no tools defined.
    """

    ml_model = "gpt-5"
    blocks = [
        TextUserMessage(
            "You are a helpful assistant. This is the second node. Please respond with 'Second node response'"
        ),
    ]
    functions = []
    prompt_inputs = {}


class ConsecutiveToolCallingNodesWorkflow(BaseWorkflow):
    """
    A workflow that uses two consecutive ToolCallingNodes with no tools defined.
    This should demonstrate the bug where the second node doesn't execute.
    """

    graph = FirstToolCallingNode >> SecondToolCallingNode

    class Outputs(BaseWorkflow.Outputs):
        text = SecondToolCallingNode.Outputs.text
        chat_history = SecondToolCallingNode.Outputs.chat_history
