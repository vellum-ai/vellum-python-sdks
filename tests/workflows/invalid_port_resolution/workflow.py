from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.constant import ConstantValueReference


class MyNode(BaseNode):
    class Ports(BaseNode.Ports):
        foo = Port.on_if(ConstantValueReference(1).contains("bar"))


class OtherNode(BaseNode):
    pass


class InvalidPortResolutionWorkflow(BaseWorkflow):
    """
    This Workflow contains an invalid port description, and should raise a user facing error.
    """

    graph = MyNode.Ports.foo >> OtherNode

    class Outputs(BaseWorkflow.Outputs):
        pass
