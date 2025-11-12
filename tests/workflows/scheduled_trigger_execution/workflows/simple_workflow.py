from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum.workflows.triggers import ScheduleTrigger


class MySchedule(ScheduleTrigger):
    class Config(ScheduleTrigger.Config):
        cron = "* * * * *"
        timezone = "UTC"


class MyNode(BaseNode):
    schedule = MySchedule.current_run_at

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=str(self.schedule))


class SimpleScheduledWorkflow(BaseWorkflow):
    """Workflow triggered by a Schedule"""

    graph = MySchedule >> MyNode

    class Outputs(BaseWorkflow.Outputs):
        result = MyNode.Outputs.result
