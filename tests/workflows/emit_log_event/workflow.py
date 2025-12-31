from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class LoggingNode(BaseNode):
    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        self._context.emit_log_event(
            severity="INFO",
            message="Custom log message",
            attributes={"key": "value", "count": 42},
            node=self,
        )
        return self.Outputs(result="done")


class EmitLogEventWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    graph = LoggingNode

    class Outputs(BaseOutputs):
        result = LoggingNode.Outputs.result
