from vellum.workflows import BaseWorkflow
from vellum.workflows.state.base import BaseState

from .nodes.agent import AgentNode, WorkflowInputs


class Workflow(BaseWorkflow[WorkflowInputs, BaseState]):
    """
    A workflow that uses a ToolCallingNode with an inline subworkflow
    containing a custom node with a custom run method.
    """

    graph = AgentNode

    class Outputs(BaseWorkflow.Outputs):
        text = AgentNode.Outputs.text
        chat_history = AgentNode.Outputs.chat_history
