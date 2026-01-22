from vellum.workflows import BaseWorkflow
from vellum.workflows.state.base import BaseState

from .inputs import WorkflowInputs
from .nodes.agent import AgentNode


class Workflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = AgentNode

    class Outputs(BaseWorkflow.Outputs):
        text = AgentNode.Outputs.text
        chat_history = AgentNode.Outputs.chat_history
