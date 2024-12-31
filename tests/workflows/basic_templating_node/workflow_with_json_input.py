from typing import Any

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import TemplatingNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json


class Inputs(BaseInputs):
    info: Any


class ExampleTemplatingNode(TemplatingNode[BaseState, Json]):
    template = "The meaning of {{ info }} is not known"

    inputs = {
        "info": Inputs.info,
    }


class BasicTemplatingNodeWorkflowWithJson(BaseWorkflow[Inputs, BaseState]):
    graph = ExampleTemplatingNode

    class Outputs(BaseOutputs):
        result = ExampleTemplatingNode.Outputs.result
