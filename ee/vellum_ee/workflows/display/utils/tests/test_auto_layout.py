from uuid import uuid4

from vellum_ee.workflows.display.base import EdgeDisplay
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.utils.auto_layout import auto_layout_nodes


def test_auto_layout_basic():
    """Test basic auto layout functionality with a simple linear graph."""
    nodes = [
        ("node1", NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=100, height=80)),
        ("node2", NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=120, height=90)),
        ("node3", NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=110, height=85)),
    ]

    edges = [
        ("node1", "node2", EdgeDisplay(id=uuid4())),
        ("node2", "node3", EdgeDisplay(id=uuid4())),
    ]

    positioned_nodes = auto_layout_nodes(nodes, edges)

    node_positions = {node_id: data.position for node_id, data in positioned_nodes}

    assert node_positions["node1"].x < node_positions["node2"].x
    assert node_positions["node2"].x < node_positions["node3"].x


def test_auto_layout_parallel_branches():
    """Test auto layout with parallel branches."""
    nodes = [
        ("start", NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=100, height=80)),
        ("branch1", NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=100, height=80)),
        ("branch2", NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=100, height=80)),
        ("end", NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=100, height=80)),
    ]

    edges = [
        ("start", "branch1", EdgeDisplay(id=uuid4())),
        ("start", "branch2", EdgeDisplay(id=uuid4())),
        ("branch1", "end", EdgeDisplay(id=uuid4())),
        ("branch2", "end", EdgeDisplay(id=uuid4())),
    ]

    positioned_nodes = auto_layout_nodes(nodes, edges)

    node_positions = {node_id: data.position for node_id, data in positioned_nodes}

    assert node_positions["start"].x < node_positions["branch1"].x
    assert node_positions["start"].x < node_positions["branch2"].x

    assert node_positions["branch1"].x == node_positions["branch2"].x
    assert node_positions["branch1"].x < node_positions["end"].x

    assert node_positions["branch1"].x < node_positions["end"].x
    assert node_positions["branch2"].x < node_positions["end"].x
