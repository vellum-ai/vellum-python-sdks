import pytest

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


def test_base_workflow__inherit_base_outputs():
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

        def run(self):
            return self.Outputs(foo="bar")

    class MyWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyNode

        class Outputs:
            output = MyNode.Outputs.foo

    # TEST that the Outputs class is a subclass of BaseOutputs
    assert issubclass(MyWorkflow.Outputs, BaseOutputs)

    # TEST that the Outputs class does not inherit from object
    assert object not in MyWorkflow.Outputs.__bases__

    workflow = MyWorkflow()
    terminal_event = workflow.run()

    # TEST that the Outputs class has the correct attributes
    assert hasattr(MyWorkflow.Outputs, "output")

    # TEST that the outputs should be correct
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs == {"output": "bar"}


def test_subworkflow__inherit_base_outputs():
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

        def run(self):
            return self.Outputs(foo="bar")

    class SubWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = StartNode

        class Outputs:
            output = StartNode.Outputs.foo

    class SubworkflowNode(InlineSubworkflowNode):
        subworkflow = SubWorkflow

    class MainWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SubworkflowNode

        class Outputs:
            output = SubworkflowNode.Outputs.output

    # TEST that the Outputs classes are subclasses of BaseOutputs
    assert issubclass(MainWorkflow.Outputs, BaseOutputs)
    assert issubclass(SubWorkflow.Outputs, BaseOutputs)

    # TEST that the Outputs classes do not inherit from object
    assert object not in MainWorkflow.Outputs.__bases__
    assert object not in SubWorkflow.Outputs.__bases__

    # TEST execution
    workflow = MainWorkflow()
    terminal_event = workflow.run()

    # TEST that the Outputs class has the correct attributes
    assert hasattr(MainWorkflow.Outputs, "output")

    # TEST that the outputs are correct
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs == {"output": "bar"}


def test_workflow__nodes_not_in_graph():
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    class NodeC(BaseNode):
        pass

    # WHEN we create a workflow with multiple unused nodes
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA
        unused_graph = {NodeB, NodeC}

    # TEST that all nodes from unused_graph are collected
    unused_graph = set(TestWorkflow.get_unused_nodes())
    assert unused_graph == {NodeB, NodeC}


def test_workflow__unused_graph():
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    class NodeC(BaseNode):
        pass

    class NodeD(BaseNode):
        pass

    class NodeE(BaseNode):
        pass

    class NodeF(BaseNode):
        pass

    # WHEN we create a workflow with unused nodes in a graph
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA
        unused_graph = {NodeB >> {NodeC >> NodeD}, NodeE, NodeF}

    # TEST that all nodes from unused_graph are collected
    unused_graph = set(TestWorkflow.get_unused_nodes())
    assert unused_graph == {NodeB, NodeC, NodeD, NodeE, NodeF}


def test_workflow__no_unused_nodes():
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    # WHEN we create a workflow with no unused nodes
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA >> NodeB

    # TEST that nodes not in the graph are empty
    nodes = set(TestWorkflow.get_unused_nodes())
    assert nodes == set()


def test_workflow__node_in_both_graph_and_unused():
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    class NodeC(BaseNode):
        pass

    # WHEN we try to create a workflow where NodeA appears in both graph and unused
    with pytest.raises(ValueError) as exc_info:

        class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
            graph = NodeA >> NodeB
            unused_graph = {NodeA >> NodeC}

    # THEN it should raise an error
    assert "Node(s) NodeA cannot appear in both graph and unused_graph" in str(exc_info.value)
