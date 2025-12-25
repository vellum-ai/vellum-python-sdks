from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node import InlinePromptNode


class FirstNode(InlinePromptNode):
    """An inline prompt node that succeeds and produces streaming output."""

    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    block_type="JINJA",
                    template="Hello world",
                ),
            ],
        ),
    ]


class SecondNode(BaseNode):
    """A node that fails after the first node succeeds."""

    first_value = FirstNode.Outputs.text

    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        raise NodeException(code=WorkflowErrorCode.USER_DEFINED_ERROR, message="Second node failed")


class ThirdNode(BaseNode):
    """A node that succeeds after the first node succeeds."""

    first_value = FirstNode.Outputs.text

    class Outputs(BaseNode.Outputs):
        value: str = "success"


class ChainedNodeRejectionWithFulfilledOutputWorkflow(BaseWorkflow):
    """
    A workflow with nodes where:
    - The first node is an inline prompt node that succeeds and produces streaming output
    - The second node fails in parallel with the third node
    - The workflow output points to the first node's output

    This tests that the workflow should be rejected (not fulfilled) when any node fails,
    even if the workflow output was already resolved from a successful node.
    """

    graph = FirstNode >> {SecondNode, ThirdNode}

    class Outputs(BaseWorkflow.Outputs):
        final_value = FirstNode.Outputs.text
