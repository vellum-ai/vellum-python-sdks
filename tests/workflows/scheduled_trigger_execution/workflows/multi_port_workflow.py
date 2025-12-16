from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.triggers import ScheduleTrigger


class MySchedule(ScheduleTrigger):
    class Config(ScheduleTrigger.Config):
        cron = "* * * * *"
        timezone = "UTC"


class MultiPortNode(BaseNode):
    """A node with multiple ports to test deduplication."""

    class Ports(BaseNode.Ports):
        port_a = Port.on_if(True)
        port_b = Port.on_else()

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="executed")


class FinalNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        final: str

    def run(self) -> Outputs:
        return self.Outputs(final="done")


class MultiPortScheduledWorkflow(BaseWorkflow):
    """Workflow with a trigger pointing to a node with multiple ports.

    This tests that nodes with multiple ports are only executed once
    when running with a trigger, not once per port.
    """

    graph = {
        MySchedule >> MultiPortNode,
        MultiPortNode.Ports.port_a >> FinalNode,
    }

    class Outputs(BaseWorkflow.Outputs):
        result = MultiPortNode.Outputs.result
        final = FinalNode.Outputs.final
