from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.conditional_router import ConditionalRouter
from .nodes.echo_request import EchoRequest
from .nodes.error_node import ErrorNode
from .nodes.exit_node import ExitNode
from .nodes.fibonacci import Fibonacci
from .nodes.get_temperature import GetTemperature
from .nodes.my_prompt import MyPrompt
from .state import State


class IndeedWorkflow(BaseWorkflow[Inputs, State]):
    graph = MyPrompt >> {
        ConditionalRouter.Ports.exit >> ExitNode,
        ConditionalRouter.Ports.unknown >> ErrorNode,
        ConditionalRouter.Ports.fibonacci >> Fibonacci >> MyPrompt,
        ConditionalRouter.Ports.echo_request >> EchoRequest >> MyPrompt,
        ConditionalRouter.Ports.get_temperature >> GetTemperature >> MyPrompt,
    }

    class Outputs(BaseWorkflow.Outputs):
        answer = ExitNode.Outputs.value
