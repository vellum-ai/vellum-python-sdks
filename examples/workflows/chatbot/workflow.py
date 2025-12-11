from vellum.workflows import BaseWorkflow

from .inputs import Inputs
from .nodes.agent import Agent
from .nodes.append_assistant_message import AppendAssistantMessage
from .nodes.append_user_message import AppendUserMessage
from .nodes.final_output import FinalOutput
from .state import State


class Workflow(BaseWorkflow[Inputs, State]):
    # Flow:
    # 1) AppendUserMessage: add the user message onto any loaded chat history
    # 2) Agent: generate a reply
    # 3) AppendAssistantMessage: add the assistant reply to chat history
    # 4) FinalOutput: emit the full chat history (showing persisted state across executions)
    graph = AppendUserMessage >> Agent >> AppendAssistantMessage >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        response = FinalOutput.Outputs.value
