from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.final_output import FinalOutput
from .nodes.function_result_context import FunctionResultContext
from .nodes.invoke_function_s_w_code import InvokeFunctionSWCode


class InvokeFunctionsWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = InvokeFunctionSWCode >> FunctionResultContext >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
