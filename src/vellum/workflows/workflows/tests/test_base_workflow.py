import pytest

from vellum.workflows.edges.edge import Edge
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


def test_workflow__single_node():
    class NodeA(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA

    nodes = set(TestWorkflow.get_nodes())
    assert nodes == {NodeA}


def test_workflow__multiple_nodes():
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {NodeA, NodeB}

    nodes = set(TestWorkflow.get_nodes())
    assert nodes == {NodeA, NodeB}


def test_workflow__single_graph():
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA >> NodeB

    nodes = set(TestWorkflow.get_nodes())
    assert nodes == {NodeA, NodeB}


def test_workflow__multiple_graphs():
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

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA >> {NodeB >> NodeC, NodeD} >> NodeE

    nodes = set(TestWorkflow.get_nodes())
    assert nodes == {NodeA, NodeB, NodeC, NodeD, NodeE}


def test_workflow__get_edges():
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

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {NodeA >> {NodeB >> NodeC, NodeD} >> NodeE}

    edges = set(TestWorkflow.get_edges())
    assert edges == {
        Edge(from_port=NodeA.Ports.default, to_node=NodeB),
        Edge(from_port=NodeB.Ports.default, to_node=NodeC),
        Edge(from_port=NodeA.Ports.default, to_node=NodeD),
        Edge(from_port=NodeC.Ports.default, to_node=NodeE),
        Edge(from_port=NodeD.Ports.default, to_node=NodeE),
    }


def test_workflow__get_unused_nodes():
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

    class NodeG(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA
        unused_graphs = {NodeB >> NodeC, NodeD >> {NodeE >> NodeF, NodeG}}

    unused_graphs = set(TestWorkflow.get_unused_nodes())
    assert unused_graphs == {NodeB, NodeC, NodeD, NodeE, NodeF, NodeG}


def test_workflow__get_unused_edges():
    """
    Test that get_unused_edges correctly identifies edges that are defined but not used in the workflow graph.
    """

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

    class NodeG(BaseNode):
        pass

    class NodeH(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA >> NodeB
        unused_graphs = {NodeC >> NodeD, NodeE >> {NodeF, NodeG} >> NodeH}

    # Collect unused edges
    unused_edges = set(TestWorkflow.get_unused_edges())

    # Expected unused edges
    expected_unused_edges = {
        Edge(from_port=NodeC.Ports.default, to_node=NodeD),
        Edge(from_port=NodeE.Ports.default, to_node=NodeF),
        Edge(from_port=NodeE.Ports.default, to_node=NodeG),
        Edge(from_port=NodeF.Ports.default, to_node=NodeH),
        Edge(from_port=NodeG.Ports.default, to_node=NodeH),
    }

    # TEST that unused edges are correctly identified
    assert unused_edges == expected_unused_edges, f"Expected {expected_unused_edges}, but got {unused_edges}"


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


def test_workflow__no_unused_edges():
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    # WHEN we create a workflow with no unused edges
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA >> NodeB

    # TEST that unused edges are empty
    edges = set(TestWorkflow.get_unused_edges())
    assert edges == set()


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
            unused_graphs = {NodeA >> NodeC}

    # THEN it should raise an error
    assert "Node(s) NodeA cannot appear in both graph and unused_graphs" in str(exc_info.value)


def test_workflow__unsupported_graph_item():
    with pytest.raises(TypeError) as exc_info:
        # GIVEN a workflow with an unsupported graph item
        class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
            graph = 1  # type: ignore

    # THEN it should raise an error
    assert "Unexpected graph type: <class 'int'>" in str(exc_info.value)
