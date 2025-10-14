from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    tags: list[str]


class ProcessTagsNode(BaseNode):
    tags = Inputs.tags

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> BaseOutputs:
        return self.Outputs(result=f"Tags: {', '.join(self.tags)}")


class TestDatasetArraySerializationWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ProcessTagsNode

    class Outputs(BaseOutputs):
        final_result = ProcessTagsNode.Outputs.result
