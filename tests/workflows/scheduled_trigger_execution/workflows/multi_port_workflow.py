from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state import BaseState
from vellum.workflows.triggers import ScheduleTrigger


class Scheduled(ScheduleTrigger):
    class Config(ScheduleTrigger.Config):
        cron = "* * * * *"
        timezone = "UTC"


class Custom(BaseNode):
    """A node with multiple ports to test deduplication."""

    class Ports(BaseNode.Ports):
        group_1_if_port = Port.on_if(ConstantValueReference("Test").equals("test"))
        group_1_else_port = Port.on_else()

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="executed")


class Error(BaseNode):
    class Outputs(BaseNode.Outputs):
        error: str

    def run(self) -> Outputs:
        return self.Outputs(error="error")


class Output(BaseNode):
    class Outputs(BaseNode.Outputs):
        output: str

    def run(self) -> Outputs:
        return self.Outputs(output="done")


class MultiPortScheduledWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Workflow with a trigger pointing to a node with multiple ports.

    This tests that nodes with multiple ports are only executed once
    when running with a trigger, not once per port.
    """

    graph = {
        Custom.Ports.group_1_if_port >> Error,
        Custom.Ports.group_1_else_port >> Output,
        Scheduled >> Custom,
    }

    class Outputs(BaseWorkflow.Outputs):
        result = Custom.Outputs.result
