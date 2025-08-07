from typing import TYPE_CHECKING, Iterator, List, Optional, Set, Type, Union

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

    def __str__(self) -> str:
        """
        Return a visual ASCII representation of the graph showing the flow structure.
        """
        if not self._edges and not self._entrypoints:
            return "Graph(empty)"

        if not self._edges:
            if len(self._entrypoints) == 1:
                port = next(iter(self._entrypoints))
                return f"Graph: {self._get_port_name(port)}"
            else:
                port_names = [self._get_port_name(port) for port in self._entrypoints]
                return f"Graph: [{', '.join(port_names)}]"

        return self._build_flow_diagram()

    def _build_flow_diagram(self) -> str:
        """Build a connected flow diagram showing the graph structure."""
        lines = ["Graph:"]

        adjacency: dict[str, list[str]] = {}
        all_nodes = set()

        for edge in self._edges:
            source_node = edge.from_port.node_class.__name__
            target_node = edge.to_node.__name__

            all_nodes.add(source_node)
            all_nodes.add(target_node)

            if source_node not in adjacency:
                adjacency[source_node] = []
            adjacency[source_node].append(target_node)

        target_nodes = set()
        for edges in adjacency.values():
            target_nodes.update(edges)

        root_nodes = []
        for port in self._entrypoints:
            node_name = port.node_class.__name__
            if node_name not in target_nodes:
                root_nodes.append(node_name)

        if not root_nodes and self._entrypoints:
            root_nodes = [next(iter(self._entrypoints)).node_class.__name__]

        visited = set()
        currently_visiting = set()

        def render_node(node: str, prefix: str = "  ", is_last: bool = True, path: Optional[List[str]] = None) -> None:
            if path is None:
                path = []

            if node in currently_visiting:
                lines.append(f"{prefix}{'└─' if is_last else '├─'} {node} ⟲ (loops back)")
                return

            if node in visited:
                lines.append(f"{prefix}{'└─' if is_last else '├─'} {node} → (see above)")
                return

            visited.add(node)
            currently_visiting.add(node)

            lines.append(f"{prefix}{'└─' if is_last else '├─'} {node}")

            if node in adjacency:
                children = adjacency[node]
                for i, child in enumerate(children):
                    child_is_last = i == len(children) - 1
                    next_prefix = prefix + ("   " if is_last else "│  ")
                    render_node(child, next_prefix, child_is_last, path + [node])

            currently_visiting.remove(node)

        for i, root in enumerate(root_nodes):
            is_last_root = i == len(root_nodes) - 1
            render_node(root, "  ", is_last_root)

        return "\n".join(lines)

    def _get_port_name(self, port: "Port") -> str:
        """Get a readable name for a port."""
        try:
            if hasattr(port, "node_class") and hasattr(port.node_class, "__name__"):
                node_name = port.node_class.__name__
                port_name = getattr(port, "name", "unknown")
                return f"{node_name}.{port_name}"
            else:
                return str(port)
        except Exception:
            return f"<Port:{getattr(port, 'name', 'unknown')}>"

    def _get_node_name(self, node: Type["BaseNode"]) -> str:
        """Get a readable name for a node."""
        try:
            return getattr(node, "__name__", str(node))
        except Exception:
            return "<Node:unknown>"
