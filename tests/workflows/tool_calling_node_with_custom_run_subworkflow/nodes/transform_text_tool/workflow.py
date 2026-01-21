from vellum.workflows import BaseWorkflow
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState

from .inputs import ToolInputs
from .nodes.transform_node import TransformNode


class TransformTextToolWorkflow(BaseWorkflow[ToolInputs, BaseState]):
    """
    A subworkflow tool that transforms text using a custom node with a custom run method.
    """

    graph = TransformNode

    class Outputs(BaseOutputs):
        result = TransformNode.Outputs.result
