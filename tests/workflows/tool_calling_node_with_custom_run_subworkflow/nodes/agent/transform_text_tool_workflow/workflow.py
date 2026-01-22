from vellum.workflows import BaseWorkflow
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState

from .inputs import Inputs
from .nodes.transform_node import TransformNode


class TransformTextToolWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = TransformNode

    class Outputs(BaseOutputs):
        result = TransformNode.Outputs.result
