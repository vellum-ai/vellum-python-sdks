import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.exceptions import WorkflowInitializationException
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
    "workflow_factory,description",
    [
        (create_empty_if_workflow, "IF"),
        (create_empty_elif_workflow, "ELIF"),
    ],
    ids=["empty_if", "empty_elif"],
)
def test_empty_conditional_ports(workflow_factory, description):
    with pytest.raises(WorkflowInitializationException) as exc_info:
        workflow_cls = workflow_factory()
        workflow_cls()

    assert str(exc_info.value) == f"Please verify that your {description} ports have defined expressions"
