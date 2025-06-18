from typing import Iterator, List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    foo: str


class StreamingNode(BaseNode):
    foo = Inputs.foo

    class Outputs(BaseNode.Outputs):
        stream: List[str]

    def run(self) -> Iterator[BaseOutput]:
        stream = []
        for i in range(3):
            chunk = f"{self.foo}, world! {i}"
            stream.append(chunk)
            yield BaseOutput(name="stream", delta=chunk)

        yield BaseOutput(name="stream", value=stream)


class BasicNodeStreaming(BaseWorkflow[Inputs, BaseState]):
    graph = StreamingNode

    class Outputs(BaseNode.Outputs):
        outer_stream = StreamingNode.Outputs.stream
