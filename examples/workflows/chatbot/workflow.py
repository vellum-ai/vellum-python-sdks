from vellum.workflows import BaseWorkflow

from .inputs import Inputs
from .nodes.chatbot_node import ChatbotNode
from .nodes.final_output import FinalOutput
from .state import State


class Workflow(BaseWorkflow[Inputs, State]):
    graph = ChatbotNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        response = FinalOutput.Outputs.value
