from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.types.core import MergeBehavior


class Inputs(BaseInputs):
    input: str


class AwaitAnyGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY
