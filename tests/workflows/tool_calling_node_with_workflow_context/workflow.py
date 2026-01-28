from vellum.workflows import BaseWorkflow

from .nodes.context_aware_tool_node import ContextAwareToolNode


class ToolCallingNodeWithWorkflowContextWorkflow(BaseWorkflow):
    graph = ContextAwareToolNode

    class Outputs(BaseWorkflow.Outputs):
        text = ContextAwareToolNode.Outputs.text
        chat_history = ContextAwareToolNode.Outputs.chat_history
