from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.triggers import ScheduleTrigger


class MyScheduleTrigger(ScheduleTrigger):
    """A schedule trigger that is NOT used in the workflow graph, only in DatasetRow."""

    class Config(ScheduleTrigger.Config):
        cron = "0 * * * *"
        timezone = "UTC"


class SimpleNode(BaseNode):
    class Outputs(BaseOutputs):
        result: str

    def run(self) -> BaseOutputs:
        return self.Outputs(result="Hello")


class TestDatasetTriggerNotInGraphWorkflow(BaseWorkflow):
    """Workflow where the trigger is NOT in the graph, only referenced in DatasetRow."""

    graph = SimpleNode

    class Outputs(BaseOutputs):
        final_result = SimpleNode.Outputs.result
