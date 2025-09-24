from typing import Any

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    string_input: str


class AnyTerminalNode(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value: Any = Inputs.string_input


class AnyTerminalNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = AnyTerminalNode

    class Outputs(BaseWorkflow.Outputs):
        value = AnyTerminalNode.Outputs.value
