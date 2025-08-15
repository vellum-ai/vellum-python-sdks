from vellum.workflows.edges.edge import Edge
from vellum.workflows.graph.graph import Graph
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port


def test_graph__from_node():
    # GIVEN a node
    class MyNode(BaseNode):
        pass

    # WHEN we create a graph from the node
    graph = Graph.from_node(MyNode)

    # THEN the graph has the node as the entrypoint
    assert set(graph.entrypoints) == {MyNode}

    # AND one node
    assert len(list(graph.nodes)) == 1

    # AND no edges
    assert len(list(graph.edges)) == 0


def test_graph__from_edge():
    # GIVEN an edge
    class SourceNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    edge = Edge(SourceNode.Ports.default, TargetNode)

    # WHEN we create a graph from the edge
    graph = Graph.from_edge(edge)

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND two nodes
    assert len(list(graph.nodes)) == 2

    # AND one edge
    assert len(list(graph.edges)) == 1


def test_graph__node_to_node():
    # GIVEN two nodes
    class SourceNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph from the source node to the target node
    graph = SourceNode >> TargetNode

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND two nodes
    assert len(list(graph.nodes)) == 2

    # AND one edge
    assert len(list(graph.edges)) == 1


def test_graph__port_to_node():
    # GIVEN a two nodes, where the source node has a port
    class SourceNode(BaseNode):
        class Ports(BaseNode.Ports):
            output = Port.on_else()

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph from the source port to the target node
    graph = SourceNode.Ports.output >> TargetNode

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND two nodes
    assert len(list(graph.nodes)) == 2

    # AND one edge
    assert len(list(graph.edges)) == 1


def test_graph__graph_to_node():
    # GIVEN three nodes
    class SourceNode(BaseNode):
        pass

    class MiddleNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph from the source node to the target node via the middle node
    graph = SourceNode >> MiddleNode >> TargetNode

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 2


def test_graph__edgeless_graph_to_node():
    # GIVEN two nodes
    class SourceNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # AND a graph of the first node
    subgraph = Graph.from_node(SourceNode)

    # WHEN we create a graph from the source graph to the target node
    graph = subgraph >> TargetNode

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND two nodes
    assert len(list(graph.nodes)) == 2

    # AND one edge
    assert len(list(graph.edges)) == 1

    # AND the first node's port has reference to the edge
    assert set(SourceNode.Ports.default.edges) == set(graph.edges)


def test_graph__edgeless_graph_to_graph():
    # GIVEN two nodes
    class SourceNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # AND a graph of the first node
    subgraph = Graph.from_node(SourceNode)

    # AND a graph of the second node
    target_subgraph = Graph.from_node(TargetNode)

    # WHEN we create a graph from the source graph to the target node
    graph = subgraph >> target_subgraph

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND two nodes
    assert len(list(graph.nodes)) == 2

    # AND one edge
    assert len(list(graph.edges)) == 1

    # AND the first node's port has reference to the edges
    assert set(SourceNode.Ports.default.edges) == set(graph.edges)


def test_graph__graph_to_edgeless_graph():
    # GIVEN three nodes
    class SourceNode(BaseNode):
        pass

    class MiddleNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # AND a graph of the first two nodes
    subgraph = SourceNode >> MiddleNode

    # AND a graph of the third node
    target_subgraph = Graph.from_node(TargetNode)

    # WHEN we create a graph from the source graph to the target node
    graph = subgraph >> target_subgraph

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 2


def test_graph__node_to_graph():
    # GIVEN three nodes
    class SourceNode(BaseNode):
        pass

    class MiddleNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # AND a graph of the last two nodes
    target_subgraph = MiddleNode >> TargetNode

    # WHEN we create a graph from the source node to the target graph
    graph = SourceNode >> target_subgraph

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 2


def test_graph__repeated_edge():
    # GIVEN two nodes
    class SourceNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph from the source node to the target node twice
    graph = SourceNode >> TargetNode >> SourceNode >> TargetNode

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND two nodes
    assert len(list(graph.nodes)) == 2

    # AND two edges
    assert len(list(graph.edges)) == 2

    # AND the first node's port has reference to just one edge
    assert len(list(SourceNode.Ports.default.edges)) == 1


def test_graph__node_to_set():
    # GIVEN three nodes, one with ports
    class SourceNode(BaseNode):
        pass

    class MiddleNode(BaseNode):
        class Ports(BaseNode.Ports):
            top = Port.on_if(SourceNode.Execution.count.less_than(1))
            bottom = Port.on_else()

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph with a set
    graph = SourceNode >> {
        MiddleNode.Ports.top >> SourceNode,
        MiddleNode.Ports.bottom >> TargetNode,
    }

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 3


def test_graph__graph_to_set():
    # GIVEN four nodes, one with ports
    class SourceNode(BaseNode):
        pass

    class SecondNode(BaseNode):
        pass

    class MiddleNode(BaseNode):
        class Ports(BaseNode.Ports):
            top = Port.on_if(SourceNode.Execution.count.less_than(1))
            bottom = Port.on_else()

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph between a graph and a set
    graph = (
        SourceNode
        >> SecondNode
        >> {
            MiddleNode.Ports.top >> SourceNode,
            MiddleNode.Ports.bottom >> TargetNode,
        }
    )

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 4

    # AND two edges
    assert len(list(graph.edges)) == 4


def test_graph__graph_set_to_set():
    # GIVEN five nodes
    class SourceNode(BaseNode):
        pass

    class TopNode(BaseNode):
        pass

    class BottomNode(BaseNode):
        pass

    class ConditionalNode(BaseNode):
        class Ports(BaseNode.Ports):
            top = Port.on_if(SourceNode.Execution.count.less_than(1))
            bottom = Port.on_else()

    class EndNode(BaseNode):
        pass

    # WHEN we create a graph that draws an edge between sets
    graph = (
        SourceNode
        >> {
            TopNode,
            BottomNode,
        }
        >> {
            ConditionalNode.Ports.top >> SourceNode,
            ConditionalNode.Ports.bottom >> EndNode,
        }
    )

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 5

    # AND two edges
    assert len(list(graph.edges)) == 6


def test_graph__port_to_graph():
    # GIVEN three nodes where the first node has a port
    class SourceNode(BaseNode):
        class Ports(BaseNode.Ports):
            custom = Port.on_else()

    class MiddleNode(BaseNode):
        pass

    class EndNode(BaseNode):
        pass

    # WHEN we create a graph from the port to a subgraph
    graph = SourceNode.Ports.custom >> (MiddleNode >> EndNode)

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 2


def test_graph__port_to_set():
    # GIVEN three nodes where the first node has a port
    class SourceNode(BaseNode):
        class Ports(BaseNode.Ports):
            custom = Port.on_else()

    class TopNode(BaseNode):
        pass

    class BottomNode(BaseNode):
        pass

    # WHEN we create a graph from the port to the set
    graph = SourceNode.Ports.custom >> {
        TopNode,
        BottomNode,
    }

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 2


def test_graph__set_to_node():
    # GIVEN three nodes
    class TopNode(BaseNode):
        pass

    class BottomNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph from a set to a node
    graph = {
        TopNode,
        BottomNode,
    } >> TargetNode

    # THEN the graph has both the top node and the bottom node as the entrypoints
    assert set(graph.entrypoints) == {TopNode, BottomNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 2


def test_graph__node_to_port():
    # GIVEN two nodes, one with a port
    class SourceNode(BaseNode):
        pass

    class MiddleNode(BaseNode):
        class Ports(BaseNode.Ports):
            custom = Port.on_else()

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph from the source node to the target node
    graph = SourceNode >> MiddleNode.Ports.custom >> TargetNode

    # THEN the graph has the source node as the entrypoint
    assert set(graph.entrypoints) == {SourceNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 2


def test_graph__set_to_graph():
    # GIVEN three nodes
    class SourceNode(BaseNode):
        pass

    class MiddleNode(BaseNode):
        pass

    class TargetNode(BaseNode):
        pass

    # WHEN we create a graph from a set to a graph
    graph: Graph = {SourceNode, MiddleNode} >> Graph.from_node(TargetNode)

    # THEN the graph has the source node and middle node as the entrypoints
    assert set(graph.entrypoints) == {SourceNode, MiddleNode}

    # AND three nodes
    assert len(list(graph.nodes)) == 3

    # AND two edges
    assert len(list(graph.edges)) == 2


def test_graph__str_simple_linear():
    # GIVEN a simple linear graph: A -> B -> C
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    class NodeC(BaseNode):
        pass

    graph = NodeA >> NodeB >> NodeC

    # WHEN we convert the graph to string
    result = str(graph)

    # THEN it shows the linear flow structure
    expected_lines = ["Graph:", "  └─ NodeA", "     └─ NodeB", "        └─ NodeC"]
    assert result == "\n".join(expected_lines)


def test_graph__str_with_branching():
    # GIVEN a graph with branching: A -> {B, C}
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    class NodeC(BaseNode):
        pass

    graph = NodeA >> {NodeB, NodeC}

    # WHEN we convert the graph to string
    result = str(graph)

    # THEN it shows the branching structure
    # Note: The order might vary due to set ordering, so we check for the structure
    lines = result.split("\n")
    assert lines[0] == "Graph:"
    assert lines[1] == "  └─ NodeA"

    # Should have two branches (order may vary)
    branch_lines = [line.strip() for line in lines[2:] if line.strip()]
    assert len(branch_lines) == 2
    assert any("NodeB" in line for line in branch_lines)
    assert any("NodeC" in line for line in branch_lines)
    assert all(line.startswith("├─ ") or line.startswith("└─ ") for line in branch_lines)


def test_graph__str_with_loop():
    # GIVEN a graph with a loop: A -> B -> A (loop back)
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    # Create the loop manually using edges
    edge1 = Edge(NodeA.Ports.default, NodeB)
    edge2 = Edge(NodeB.Ports.default, NodeA)

    graph = Graph(entrypoints={NodeA.Ports.default}, edges=[edge1, edge2], terminals={NodeA.Ports.default})

    # WHEN we convert the graph to string
    result = str(graph)

    # THEN it shows the loop with cycle detection
    expected_lines = ["Graph:", "  └─ NodeA", "     └─ NodeB", "        └─ NodeA ⟲ (loops back)"]
    assert result == "\n".join(expected_lines)


def test_graph__str_empty_graph():
    # GIVEN an empty graph
    graph = Graph(entrypoints=set(), edges=[], terminals=set())

    # WHEN we convert the graph to string
    result = str(graph)

    # THEN it shows empty graph message
    assert result == "Graph(empty)"


def test_graph__str_single_node():
    # GIVEN a graph with just one node and no edges
    class SingleNode(BaseNode):
        pass

    graph = Graph.from_node(SingleNode)

    # WHEN we convert the graph to string
    result = str(graph)

    # THEN it shows the single node
    assert "SingleNode.default" in result
    assert "Graph:" in result


def test_graph__from_node_with_empty_ports():
    """
    Tests that building a graph from a single node with empty Ports class generates 1 node.
    """

    # GIVEN a node with an empty Ports class
    class NodeWithEmptyPorts(BaseNode):
        class Ports(BaseNode.Ports):
            pass

    # WHEN we create a graph from the node
    graph = Graph.from_node(NodeWithEmptyPorts)

    # THEN the graph should have exactly 1 node
    assert len(list(graph.nodes)) == 1
