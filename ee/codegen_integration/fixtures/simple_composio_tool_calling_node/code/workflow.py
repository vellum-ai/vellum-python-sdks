from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import ComposioToolDefinition
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow


class Inputs(BaseInputs):
    query: str


class ComposioToolCallingNode(ToolCallingNode):
    """
    A tool calling node that uses a ComposioTool for GitHub issue creation.
    """

    ml_model = "gpt-4o-mini"
    functions = [
        ComposioToolDefinition(
            toolkit="GITHUB",
            action="GITHUB_CREATE_AN_ISSUE",
            description="Create a new issue in a GitHub repository",
            display_name="Create GitHub Issue",
            user_id=None,
        )
    ]


class Workflow(BaseWorkflow[Inputs, BaseState]):
    """
    A workflow that uses ComposioToolDefinition in a tool calling node.
    """

    graph = ComposioToolCallingNode

    class Outputs(BaseWorkflow.Outputs):
        text = ComposioToolCallingNode.Outputs.text
        chat_history = ComposioToolCallingNode.Outputs.chat_history
