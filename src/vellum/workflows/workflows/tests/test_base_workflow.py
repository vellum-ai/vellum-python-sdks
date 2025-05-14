import pytest
from uuid import UUID, uuid4

from vellum.workflows.edges.edge import Edge
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.stack import Stack
from vellum.workflows.workflows.base import BaseWorkflow


class GlobalTestWorkflow(BaseWorkflow):
    """
    Used as part of `test_base_workflow__deserialize_state_with_invalid_workflow_definition` below.
    """

    pass


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


def test_base_workflow__deserialize_state():
    # GIVEN a state definition
    class State(BaseState):
        bar: str

    # AND an inputs definition
    class Inputs(BaseInputs):
        baz: str

    # AND a node
    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a node id for node A
    node_a_id = uuid4()
    NodeA.__id__ = node_a_id

    # AND an output id for NodeA.Outputs.foo
    node_a_output_id = uuid4()
    NodeA.__output_ids__["foo"] = node_a_output_id

    # AND a workflow that uses all three
    class TestWorkflow(BaseWorkflow[Inputs, State]):
        graph = NodeA

    # WHEN we deserialize the state
    last_span_id = str(uuid4())
    state = TestWorkflow.deserialize_state(
        {
            "bar": "My state bar",
            "meta": {
                "id": "b70a5a4f-8253-4a38-aeaf-0700b4783a78",
                "trace_id": "9dcfb309-81e9-4b75-9b21-edd31cf9685f",
                "span_id": "1c2e310c-3624-4f4f-b7ac-1e429de29bbf",
                "updated_ts": "2025-04-14T19:22:18.504902",
                "external_inputs": {},
                "node_outputs": {
                    str(node_a_output_id): "My node A output foo",
                },
                "node_execution_cache": {
                    "dependencies_invoked": {
                        last_span_id: [],
                    },
                    "node_executions_initiated": {
                        str(node_a_id): [last_span_id],
                    },
                    "node_executions_fulfilled": {
                        str(node_a_id): [last_span_id],
                    },
                    "node_executions_queued": {
                        str(node_a_id): [],
                    },
                },
                "parent": None,
            },
        },
        workflow_inputs=Inputs(baz="My input baz"),
    )

    # THEN the state should be correct
    assert state.bar == "My state bar"
    assert state.meta.node_outputs == {NodeA.Outputs.foo: "My node A output foo"}
    assert isinstance(state.meta.workflow_inputs, Inputs)
    assert state.meta.workflow_inputs.baz == "My input baz"

    # AND the node execution cache should deserialize correctly
    assert state.meta.node_execution_cache._node_executions_initiated == {NodeA: {UUID(last_span_id)}}
    assert state.meta.node_execution_cache._node_executions_fulfilled == {NodeA: Stack.from_list([UUID(last_span_id)])}
    assert state.meta.node_execution_cache._node_executions_queued == {NodeA: []}
    assert state.meta.node_execution_cache._dependencies_invoked == {UUID(last_span_id): set()}


def test_base_workflow__deserialize_legacy_node_execution_cache():

    # GIVEN a state definition
    class State(BaseState):
        bar: str

    # AND a node
    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow that uses both
    class TestWorkflow(BaseWorkflow[BaseInputs, State]):
        graph = NodeA

    # WHEN we deserialize the state that had a legacy node execution cache format
    last_span_id = str(uuid4())
    node_a_full_name = "vellum.workflows.workflows.tests.test_base_workflow.test_base_workflow__deserialize_legacy_node_execution_cache.<locals>.NodeA"  # noqa: E501
    state = TestWorkflow.deserialize_state(
        {
            "meta": {
                "node_execution_cache": {
                    "dependencies_invoked": {
                        last_span_id: [],
                    },
                    "node_executions_initiated": {
                        node_a_full_name: [last_span_id],
                    },
                    "node_executions_fulfilled": {
                        node_a_full_name: [last_span_id],
                    },
                    "node_executions_queued": {
                        node_a_full_name: [],
                    },
                },
            },
        },
    )

    # THEN the node execution cache should deserialize correctly
    assert state.meta.node_execution_cache._node_executions_initiated == {NodeA: {UUID(last_span_id)}}
    assert state.meta.node_execution_cache._node_executions_fulfilled == {NodeA: Stack.from_list([UUID(last_span_id)])}
    assert state.meta.node_execution_cache._node_executions_queued == {NodeA: []}
    assert state.meta.node_execution_cache._dependencies_invoked == {UUID(last_span_id): set()}


def test_base_workflow__deserialize_legacy_node_outputs():

    # GIVEN a state definition
    class State(BaseState):
        bar: str

    # AND a node
    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow that uses both
    class TestWorkflow(BaseWorkflow[BaseInputs, State]):
        graph = NodeA

    # WHEN we deserialize the state that had a legacy node execution cache format
    state = TestWorkflow.deserialize_state(
        {
            "meta": {
                "node_outputs": {
                    "test_base_workflow__deserialize_legacy_node_outputs.<locals>.NodeA.Outputs.foo": "My node A output foo",  # noqa: E501
                },
            },
        },
    )

    # THEN the node execution cache should deserialize correctly
    assert state.meta.node_outputs == {NodeA.Outputs.foo: "My node A output foo"}


def test_base_workflow__deserialize_state_with_optional_inputs():

    # GIVEN a state definition
    class State(BaseState):
        bar: str

    # AND an inputs definition with an optional field
    class Inputs(BaseInputs):
        baz: str = "My default baz"

    # AND a node
    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow that uses all three
    class TestWorkflow(BaseWorkflow[Inputs, State]):
        graph = NodeA

    # WHEN we deserialize the state
    state = TestWorkflow.deserialize_state(
        {
            "bar": "My state bar",
            "meta": {
                "node_outputs": {},
                "parent": None,
            },
        },
    )

    # THEN the state should be correct
    assert state.bar == "My state bar"
    assert isinstance(state.meta.workflow_inputs, Inputs)
    assert state.meta.workflow_inputs.baz == "My default baz"


def test_base_workflow__deserialize_nested_state():
    # GIVEN a state definition
    class State(BaseState):
        foo: str

    # AND a nested state definition
    class NestedState(BaseState):
        bar: str

    # AND an inner node
    class InnerNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            baz: str

    # AND a subworkflow definition with the nested state and inner node
    class InnerWorkflow(BaseWorkflow[BaseInputs, NestedState]):
        graph = InnerNode

    # AND a subworkflow node
    class OuterNode(InlineSubworkflowNode[State, BaseInputs, NestedState]):
        subworkflow = InnerWorkflow

        class Outputs(InlineSubworkflowNode.Outputs):
            qux: str

    # AND a workflow that uses the outer state and subworkflow node
    class TestWorkflow(BaseWorkflow[BaseInputs, State]):
        graph = OuterNode

    # WHEN we deserialize the nested state
    inner_node_output_definition = "test_base_workflow__deserialize_nested_state.<locals>.InnerNode.Outputs.baz"
    outer_node_output_definition = "test_base_workflow__deserialize_nested_state.<locals>.OuterNode.Outputs.qux"
    state = InnerWorkflow.deserialize_state(
        {
            "bar": "My nested state bar",
            "meta": {
                "workflow_definition": {
                    "id": str(InnerWorkflow.__id__),
                    "name": "test_base_workflow__deserialize_nested_state.<locals>.InnerWorkflow",
                    "module": ["vellum", "workflows", "workflows", "tests", "test_base_workflow"],
                },
                "node_outputs": {inner_node_output_definition: "My inner node output baz"},
                "parent": {
                    "foo": "My outer state foo",
                    "meta": {
                        "node_outputs": {outer_node_output_definition: "My outer node output qux"},
                        "workflow_definition": {
                            "id": str(TestWorkflow.__id__),
                            "name": "test_base_workflow__deserialize_nested_state.<locals>.TestWorkflow",
                            "module": ["vellum", "workflows", "workflows", "tests", "test_base_workflow"],
                        },
                    },
                },
            },
        },
    )

    # THEN the state should be correct
    assert state.bar == "My nested state bar"
    assert state.meta.node_outputs == {InnerNode.Outputs.baz: "My inner node output baz"}
    assert state.meta.workflow_definition == InnerWorkflow

    # AND the parent state should be correct
    assert isinstance(state.meta.parent, State)
    assert state.meta.parent.foo == "My outer state foo"
    assert state.meta.parent.meta.node_outputs == {OuterNode.Outputs.qux: "My outer node output qux"}
    assert state.meta.parent.meta.workflow_definition == TestWorkflow


def test_base_workflow__deserialize_state_with_none():

    # GIVEN a state definition
    class State(BaseState):
        bar: str

    # AND an inputs definition
    class Inputs(BaseInputs):
        baz: str

    # AND a node
    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow that uses all three
    class TestWorkflow(BaseWorkflow[Inputs, State]):
        graph = NodeA

    # WHEN we deserialize None
    state = TestWorkflow.deserialize_state(None)

    # THEN we should get back None
    assert state is None


@pytest.mark.parametrize(
    "raw_workflow_definition",
    [
        {
            "name": "test_base_workflow__deserialize_state_with_invalid_workflow_definition.<locals>.TestWorkflow",
            "module": ["invalid", "module", "path"],
        },
        {
            "name": "test_base_workflow__deserialize_state_with_invalid_workflow_definition.<locals>.InvalidWorkflow",
            "module": ["vellum", "workflows", "workflows", "tests", "test_base_workflow"],
        },
        {
            "name": "invalid_local_function_name.<locals>.TestWorkflow",
            "module": ["vellum", "workflows", "workflows", "tests", "test_base_workflow"],
        },
        {
            "name": "GlobalTestWorkflow",
            "module": ["invalid", "module", "path"],
        },
        {
            "name": "InlineSubworkflowNode",
            "module": ["vellum", "workflows", "workflows", "tests", "test_base_workflow"],
        },
        {
            "name": "InvalidWorkflow",
            "module": ["vellum", "workflows", "workflows", "tests", "test_base_workflow"],
        },
    ],
    ids=[
        "invalid_module_path_with_locals",
        "invalid_local_name",
        "invalid_local_container",
        "invalid_global_module",
        "invalid_global_name",
        "missing_global_name",
    ],
)
def test_base_workflow__deserialize_state_with_invalid_workflow_definition(raw_workflow_definition):

    # GIVEN a state definition
    class State(BaseState):
        bar = "My default bar"

    # AND a workflow
    class TestWorkflow(BaseWorkflow[BaseInputs, State]):
        pass

    # WHEN we deserialize a state with an invalid module path
    state = TestWorkflow.deserialize_state(
        {
            "meta": {
                "workflow_definition": {
                    "id": str(TestWorkflow.__id__),
                    **raw_workflow_definition,
                },
            },
        },
    )

    # THEN we should get back the default state
    assert isinstance(state, State)
    assert state.bar == "My default bar"

    # AND the workflow definition should be BaseWorkflow
    assert state.meta.workflow_definition == BaseWorkflow
