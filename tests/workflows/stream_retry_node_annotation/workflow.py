from typing import Iterator, List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.outputs.base import BaseOutput


class Inputs(BaseInputs):
    items: List[str]


@RetryNode.wrap()
class InnerNode(BaseNode):
    items = Inputs.items

    class Outputs(BaseNode.Outputs):
        processed: List[str]

    def run(self) -> Iterator[BaseOutput]:
        processed_fruits = []
        for item in self.items:
            processed = item + " " + item
            processed_fruits.append(processed)
            yield BaseOutput(delta=processed, name="processed")

        yield BaseOutput(value=processed_fruits, name="processed")


class StreamingRetryExample(BaseWorkflow):
    """
    This Workflow ensures that we support streaming within the context of a Node wrapped in a RetryNode.
    """

    graph = InnerNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = InnerNode.Outputs.processed
