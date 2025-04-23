import random

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.workflows.base import BaseWorkflow


@TryNode.wrap()
class ThresholdNode(BaseNode):
    class Ports(BaseNode.Ports):
        failed = Port.on_if(LazyReference(lambda: ThresholdNode.Outputs.error.is_not_undefined()))

    class Outputs(BaseNode.Outputs):
        message: str

    def run(self) -> Outputs:
        threshold = random.randint(0, 100)
        if threshold > 50:
            raise NodeException(
                code=WorkflowErrorCode.USER_DEFINED_ERROR,
                message="Threshold exceeded",
            )

        return self.Outputs(message=f"Threshold: {threshold}")


class FormatErrorNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        message = ThresholdNode.Outputs.error["message"]


class TryNodePortsWorkflow(BaseWorkflow):
    graph = ThresholdNode.Ports.failed >> FormatErrorNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = ThresholdNode.Outputs.message.coalesce(FormatErrorNode.Outputs.message)
