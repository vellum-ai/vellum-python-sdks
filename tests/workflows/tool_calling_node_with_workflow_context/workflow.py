from vellum.workflows import BaseWorkflow

from .nodes.workflow import ContextAwareToolNode


class ToolCallingNodeWithWorkflowContextWorkflow(BaseWorkflow):
    graph = ContextAwareToolNode

    class Outputs(BaseWorkflow.Outputs):
        text = ContextAwareToolNode.Outputs.text
        chat_history = ContextAwareToolNode.Outputs.chat_history
