from vellum.workflows import BaseWorkflow, ScheduleTrigger
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode


class Inputs(BaseInputs):
    required_value: str


class MySchedule(ScheduleTrigger):
    class Config(ScheduleTrigger.Config):
        cron = "* * * * *"
        timezone = "UTC"


class StartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        message: str

    def run(self) -> Outputs:
        return StartNode.Outputs(message="hello from trigger")


class TriggerRequiredInputsWorkflow(BaseWorkflow):
    graph = MySchedule >> StartNode

    class Outputs(BaseWorkflow.Outputs):
        message = StartNode.Outputs.message
