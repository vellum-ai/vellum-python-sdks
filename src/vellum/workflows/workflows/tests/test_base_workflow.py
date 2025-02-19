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
        unused_graphs = {NodeB, NodeC}

    # TEST that all nodes from unused_graphs are collected
    unused_graphs = set(TestWorkflow.get_unused_nodes())
    assert unused_graphs == {NodeB, NodeC}


def test_workflow__unused_graphs():
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
        unused_graphs = {NodeB >> {NodeC >> NodeD}, NodeE, NodeF}

    # TEST that all nodes from unused_graphs are collected
    unused_graphs = set(TestWorkflow.get_unused_nodes())
    assert unused_graphs == {NodeB, NodeC, NodeD, NodeE, NodeF}


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
            unused_graphs = {NodeA >> NodeC}

    # THEN it should raise an error
    assert "Node(s) NodeA cannot appear in both graph and unused_graphs" in str(exc_info.value)


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

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NodeA >> NodeB
        unused_graphs = {NodeC >> {NodeD >> NodeE, NodeF} >> NodeG}

    edge_c_to_d = Edge(from_port=NodeC.Ports.default, to_node=NodeD)
    edge_c_to_f = Edge(from_port=NodeC.Ports.default, to_node=NodeF)
    edge_d_to_e = Edge(from_port=NodeD.Ports.default, to_node=NodeE)
    edge_e_to_g = Edge(from_port=NodeE.Ports.default, to_node=NodeG)
    edge_f_to_g = Edge(from_port=NodeF.Ports.default, to_node=NodeG)

    # Collect unused edges
    unused_edges = set(TestWorkflow.get_unused_edges())

    # Expected unused edges
    expected_unused_edges = {edge_c_to_d, edge_c_to_f, edge_d_to_e, edge_e_to_g, edge_f_to_g}

    # TEST that unused edges are correctly identified
    assert unused_edges == expected_unused_edges, f"Expected {expected_unused_edges}, but got {unused_edges}"
