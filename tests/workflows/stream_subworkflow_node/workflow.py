from typing import Iterator, List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node import InlineSubworkflowNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    items: List[str]


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


class InnerWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = InnerNode

    class Outputs(BaseWorkflow.Outputs):
        processed = InnerNode.Outputs.processed


class SubworkflowNode(InlineSubworkflowNode[BaseState, Inputs, BaseState]):
    subworkflow_inputs = {"items": Inputs.items}  # type: ignore[dict-item]
    subworkflow = InnerWorkflow

    class Outputs(InlineSubworkflowNode.Outputs):
        processed = InnerWorkflow.Outputs.processed


class StreamingInlineSubworkflowExample(BaseWorkflow[Inputs, BaseState]):
    """
    This Workflow ensures that we support streaming within the context of an InlineSubworkflowNode.
    """

    graph = SubworkflowNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = SubworkflowNode.Outputs.processed
