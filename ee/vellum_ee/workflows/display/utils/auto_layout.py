from collections import defaultdict
from typing import Dict, List, Set, Tuple

from vellum_ee.workflows.display.base import EdgeDisplay
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition


def auto_layout_nodes(
    nodes: List[Tuple[str, NodeDisplayData]],
    edges: List[Tuple[str, str, EdgeDisplay]],
    node_spacing: float = 150.0,
    layer_spacing: float = 200.0,
) -> List[Tuple[str, NodeDisplayData]]:
    """
    Auto-layout nodes in a hierarchical left-to-right arrangement.

    Args:
        nodes: List of (node_id, NodeDisplayData) tuples
        edges: List of (source_node_id, target_node_id, EdgeDisplay) tuples
        node_spacing: Vertical spacing between nodes in the same layer
        layer_spacing: Horizontal spacing between layers

    Returns:
        List of (node_id, NodeDisplayData) tuples with updated positions
    """
    if not nodes:
        return []

    node_dict = {node_id: data for node_id, data in nodes}

    graph: Dict[str, List[str]] = defaultdict(list)
    in_degree: Dict[str, int] = defaultdict(int)
    all_nodes = set(node_dict.keys())

    for source, target, _ in edges:
        if source in all_nodes and target in all_nodes:
            graph[source].append(target)
            in_degree[target] += 1

    for node_id in all_nodes:
        if node_id not in in_degree:
            in_degree[node_id] = 0

    layers = _topological_sort_layers(graph, in_degree, all_nodes)

    positioned_nodes = []
    current_x = 0.0

    for layer in layers:
        if not layer:
            continue

        layer_nodes = [(node_id, node_dict[node_id]) for node_id in layer]
        total_height = _calculate_layer_height(layer_nodes, node_spacing)

        current_y = -total_height / 2.0

        for node_id in layer:
            node_data = node_dict[node_id]
            node_height = node_data.height or 100.0

            new_position = NodeDisplayPosition(x=current_x, y=current_y)

            updated_data = NodeDisplayData(
                position=new_position, width=node_data.width, height=node_data.height, comment=node_data.comment
            )

            positioned_nodes.append((node_id, updated_data))
            current_y += node_height + node_spacing

        current_x += layer_spacing

    return positioned_nodes


def _topological_sort_layers(
    graph: Dict[str, List[str]], in_degree: Dict[str, int], all_nodes: Set[str]
) -> List[List[str]]:
    """
    Perform topological sorting and group nodes into layers.

    Returns:
        List of layers, where each layer is a list of node IDs
    """
    layers = []
    remaining_nodes = set(all_nodes)

    while remaining_nodes:
        current_layer = []
        for node in remaining_nodes:
            if in_degree[node] == 0:
                current_layer.append(node)

        if not current_layer:
            current_layer = [next(iter(remaining_nodes))]

        layers.append(current_layer)

        for node in current_layer:
            remaining_nodes.remove(node)
            for neighbor in graph[node]:
                if neighbor in remaining_nodes:
                    in_degree[neighbor] -= 1

    return [sorted(layer) for layer in layers]


def _calculate_layer_height(layer_nodes: List[Tuple[str, NodeDisplayData]], node_spacing: float) -> float:
    """
    Calculate the total height needed for a layer of nodes.

    Args:
        layer_nodes: List of (node_id, NodeDisplayData) tuples in the layer
        node_spacing: Spacing between nodes

    Returns:
        Total height needed for the layer
    """
    if not layer_nodes:
        return 0.0

    total_height = 0.0
    for i, (_, node_data) in enumerate(layer_nodes):
        node_height = node_data.height or 100.0
        total_height += node_height

        if i < len(layer_nodes) - 1:
            total_height += node_spacing

    return total_height
