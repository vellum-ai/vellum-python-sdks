import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import NodePorts, Port
from vellum.workflows.state import BaseState


# Had to do it this way since pytest's exception manager doesn't catch if
# I created the workflow and imported it/created it
def create_empty_if_workflow():
    class Inputs(BaseInputs):
        pass

    class EmptyIfNode(BaseNode):
        class Ports(NodePorts):
            if_branch: Port = Port.on_if()
            else_branch: Port = Port.on_else()

    class EmptyIfWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = EmptyIfNode

    return EmptyIfWorkflow


def create_empty_elif_workflow():
    class Inputs(BaseInputs):
        value: str

    class EmptyElIfNode(BaseNode):
        class Ports(NodePorts):
            if_branch: Port = Port.on_if(Inputs.value.equals("foo"))
            elif_branch: Port = Port.on_elif()
            else_branch: Port = Port.on_else()

    class EmptyElIfWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = EmptyElIfNode

    return EmptyElIfWorkflow


@pytest.mark.parametrize(
    "workflow_factory,port_name",
    [
        (create_empty_if_workflow, "if_branch"),
        (create_empty_elif_workflow, "elif_branch"),
    ],
    ids=["empty_if", "empty_elif"],
)
def test_empty_conditional_ports(workflow_factory, port_name):
    # GIVEN a workflow with an empty conditional port
    workflow_cls = workflow_factory()
    workflow = workflow_cls()

    # THEN the workflow should be created successfully
    assert workflow is not None

    node_cls = workflow_cls.graph
    test_state = BaseState()
    empty_port = getattr(node_cls.Ports, port_name)

    # THEN the port should resolve to False
    assert empty_port.resolve_condition(test_state) is False
