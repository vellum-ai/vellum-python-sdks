from vellum.workflows import BaseWorkflow
from vellum.workflows.emitters.vellum_emitter import VellumEmitter
from vellum.workflows.resolvers.resolver import VellumResolver

from .inputs import Inputs
from .nodes.chatbot_node import ChatbotNode
from .nodes.final_output import FinalOutput
from .state import State


class Workflow(BaseWorkflow[Inputs, State]):
    graph = ChatbotNode >> FinalOutput

    emitters = [VellumEmitter()]
    resolvers = [VellumResolver()]

    class Outputs(BaseWorkflow.Outputs):
        response = FinalOutput.Outputs.value
