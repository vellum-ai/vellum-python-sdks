from typing import TYPE_CHECKING, Iterator, List, Set, Type, Union

from orderly_set import OrderedSet

from vellum.workflows.edges.edge import Edge
from vellum.workflows.types.generics import NodeType

if TYPE_CHECKING:
    from vellum.workflows.nodes.bases.base import BaseNode
    from vellum.workflows.ports.port import Port

GraphTargetOfSets = Union[
    Set[NodeType],
    Set["Graph"],
    Set["Port"],
    Set[Union[Type["BaseNode"], "Graph", "Port"]],
]

GraphTarget = Union[
    Type["BaseNode"],
    "Port",
    "Graph",
    GraphTargetOfSets,
]


class Graph:
    _entrypoints: Set["Port"]
    _edges: List[Edge]
    _terminals: Set["Port"]

    def __init__(self, entrypoints: Set["Port"], edges: List[Edge], terminals: Set["Port"]):
        self._edges = edges
        self._entrypoints = entrypoints
        self._terminals = terminals

    @staticmethod
    def from_port(port: "Port") -> "Graph":
        ports = {port}
        return Graph(entrypoints=ports, edges=[], terminals=ports)

    @staticmethod
    def from_node(node: Type["BaseNode"]) -> "Graph":
        ports = {port for port in node.Ports}
        return Graph(entrypoints=ports, edges=[], terminals=ports)

    @staticmethod
    def from_set(targets: GraphTargetOfSets) -> "Graph":
        entrypoints = set()
        edges = OrderedSet[Edge]()
        terminals = set()

        for target in targets:
            if isinstance(target, Graph):
                entrypoints.update(target._entrypoints)
                edges.update(target._edges)
                terminals.update(target._terminals)
            elif hasattr(target, "Ports"):
                entrypoints.update({port for port in target.Ports})
                terminals.update({port for port in target.Ports})
            else:
                # target is a Port
                entrypoints.update({target})
                terminals.update({target})

        return Graph(entrypoints=entrypoints, edges=list(edges), terminals=terminals)

    @staticmethod
    def from_edge(edge: Edge) -> "Graph":
        return Graph(entrypoints={edge.from_port}, edges=[edge], terminals={port for port in edge.to_node.Ports})

    def __rshift__(self, other: GraphTarget) -> "Graph":
        if not self._edges and not self._entrypoints:
            raise ValueError("Graph instance can only create new edges from nodes within existing edges")

        if isinstance(other, set):
            new_terminals = set()
            for elem in other:
                for final_output_node in self._terminals:
                    if isinstance(elem, Graph):
                        midgraph = final_output_node >> set(elem.entrypoints)
                        self._extend_edges(midgraph.edges)
                        self._extend_edges(elem.edges)
                        for other_terminal in elem._terminals:
                            new_terminals.add(other_terminal)
                    elif hasattr(elem, "Ports"):
                        midgraph = final_output_node >> elem
                        self._extend_edges(midgraph.edges)
                        for other_terminal in elem.Ports:
                            new_terminals.add(other_terminal)
                    else:
                        # elem is a Port
                        midgraph = final_output_node >> elem
                        self._extend_edges(midgraph.edges)
                        new_terminals.add(elem)
            self._terminals = new_terminals
            return self

        if isinstance(other, Graph):
            for final_output_node in self._terminals:
                midgraph = final_output_node >> set(other.entrypoints)
                self._extend_edges(midgraph.edges)
                self._extend_edges(other.edges)
            self._terminals = other._terminals
            return self

        if hasattr(other, "Ports"):
            for final_output_node in self._terminals:
                subgraph = final_output_node >> other
                self._extend_edges(subgraph.edges)
            self._terminals = {port for port in other.Ports}
            return self

        # other is a Port
        for final_output_node in self._terminals:
            subgraph = final_output_node >> other
            self._extend_edges(subgraph.edges)
        self._terminals = {other}
        return self

    def __rrshift__(cls, other_cls: GraphTarget) -> "Graph":
        if not isinstance(other_cls, set):
            other_cls = {other_cls}

        return Graph.from_set(other_cls) >> cls

    @property
    def entrypoints(self) -> Iterator[Type["BaseNode"]]:
        return iter(e.node_class for e in self._entrypoints)

    @property
    def edges(self) -> Iterator[Edge]:
        return iter(self._edges)

    @property
    def nodes(self) -> Iterator[Type["BaseNode"]]:
        nodes = set()
        if not self._edges:
            for node in self.entrypoints:
                if node not in nodes:
                    nodes.add(node)
                    yield node
            return

        for edge in self._edges:
            if edge.from_port.node_class not in nodes:
                nodes.add(edge.from_port.node_class)
                yield edge.from_port.node_class
            if edge.to_node not in nodes:
                nodes.add(edge.to_node)
                yield edge.to_node

    def _extend_edges(self, edges: Iterator[Edge]) -> None:
        for edge in edges:
            if edge not in self._edges:
                self._edges.append(edge)
