from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port

from .my_prompt import MyPrompt


class ConditionalRouter(BaseNode):
    class Ports(BaseNode.Ports):
        exit = Port.on_if(MyPrompt.Outputs.results[0]["type"].equals("STRING"))
        get_temperature = Port.on_elif(MyPrompt.Outputs.results[0]["value"]["name"].equals("get_temperature"))
        echo_request = Port.on_elif(MyPrompt.Outputs.results[0]["value"]["name"].equals("echo_request"))
        fibonacci = Port.on_elif(MyPrompt.Outputs.results[0]["value"]["name"].equals("fibonacci"))
        unknown = Port.on_else()
