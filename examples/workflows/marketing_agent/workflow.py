from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.code_execution_node_9 import CodeExecutionNode9
from .nodes.email_sender import EmailSender
from .nodes.final_output import FinalOutput
from .nodes.linkedin_posting_agent import LinkedinPostingAgent
from .nodes.merge_node import MergeNode
from .nodes.tool_calling_node import ToolCallingNode as ToolCallingNodeToolCallingNode
from .nodes.tool_calling_node_1 import ToolCallingNode


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = ToolCallingNode >> FinalOutput
    unused_graphs = {CodeExecutionNode9, MergeNode, ToolCallingNodeToolCallingNode, LinkedinPostingAgent, EmailSender}

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
