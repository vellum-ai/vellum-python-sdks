from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.accumulate_chat_history import AccumulateChatHistory
from .nodes.conditional_node import ConditionalNode
from .nodes.conditional_node_10 import ConditionalNode10
from .nodes.error_node import ErrorNode
from .nodes.final_accumulation_of_chat_history import FinalAccumulationOfChatHistory
from .nodes.final_output import FinalOutput
from .nodes.get_current_weather import GetCurrentWeather
from .nodes.output_type import OutputType
from .nodes.parse_function_call import ParseFunctionCall
from .nodes.prompt_node import PromptNode


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = (
        PromptNode
        >> OutputType
        >> {
            ConditionalNode10.Ports.branch_1
            >> ParseFunctionCall
            >> {
                ConditionalNode.Ports.branch_1 >> GetCurrentWeather >> AccumulateChatHistory >> PromptNode,
                ConditionalNode.Ports.branch_2 >> ErrorNode,
            },
            ConditionalNode10.Ports.branch_2 >> FinalAccumulationOfChatHistory >> FinalOutput,
        }
    )

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
