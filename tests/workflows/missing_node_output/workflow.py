from typing import Iterator, Optional

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.types import MergeBehavior
from vellum.workflows.workflows.base import BaseWorkflow


class StartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        found_value: Optional[str]
        missing_value: Optional[str]

    def run(self) -> Iterator[BaseOutput]:
        yield BaseOutput(name="found_value", value="hello")


class NextNode(BaseNode):
    found_value = StartNode.Outputs.found_value
    missing_value = StartNode.Outputs.missing_value

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Outputs(BaseNode.Outputs):
        final_value: str

    def run(self) -> Outputs:
        return self.Outputs(final_value=f"{self.found_value} {self.missing_value}")


class MissingNodeOutputWorkflow(BaseWorkflow):
    graph = StartNode >> NextNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = NextNode.Outputs.final_value
