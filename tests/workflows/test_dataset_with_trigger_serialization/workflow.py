from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.triggers import ScheduleTrigger


class MySchedule(ScheduleTrigger):
    class Config(ScheduleTrigger.Config):
        cron = "* * * * *"
        timezone = "UTC"


class SimpleNode(BaseNode):
    message = MySchedule.current_run_at

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> BaseOutputs:
        return self.Outputs(result=f"Current run at: {str(self.message)}")


class TestDatasetWithTriggerSerializationWorkflow(BaseWorkflow):
    graph = MySchedule >> SimpleNode

    class Outputs(BaseOutputs):
        final_result = SimpleNode.Outputs.result
