import pytest
from uuid import UUID

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.constant import ConstantValueReference
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import WorkflowDisplayContext


@pytest.fixture
def node_with_implicit_properties():
    class MyNode(BaseNode):
        pass

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        pass

    expected_id = UUID("8628fe5e-620d-4935-92f1-a9ed7ed7fd92")

    return MyNodeDisplay, expected_id


@pytest.fixture
def node_with_explicit_properties():
    explicit_id = UUID("a422f67a-1d37-43f0-bdfc-1e4618c9496d")

    class MyNode(BaseNode):
        pass

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        node_id = explicit_id

    return MyNodeDisplay, explicit_id


@pytest.fixture(
    params=[
        "node_with_implicit_properties",
        "node_with_explicit_properties",
    ]
)
def node_info(request):
    return request.getfixturevalue(request.param)


def test_get_id(node_info):
    node_display, expected_id = node_info

    assert node_display().node_id == expected_id
    assert node_display.infer_node_class().__id__ == expected_id


def test_serialize_condition__accessor_expression():
    # GIVEN a node with an accessor expression in a Port
    class MyNode(BaseNode):

        class Ports(BaseNode.Ports):
            foo = Port.on_if(ConstantValueReference({"hello": "world"})["hello"])

    # WHEN we serialize the node
    node_display_class = get_node_display_class(MyNode)
    data = node_display_class().serialize(WorkflowDisplayContext())

    # THEN the condition should be serialized correctly
    assert data["ports"] == [
        {
            "id": "c5a19e2d-3476-4d51-ae8f-a00f101dec30",
            "name": "foo",
            "type": "IF",
            "expression": {
                "type": "BINARY_EXPRESSION",
                "lhs": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "JSON",
                        "value": {"hello": "world"},
                    },
                },
                "operator": "accessField",
                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "hello"}},
            },
        }
    ]


def test_serialize_display_data():
    # GIVEN a node with an accessor expression in a Port
    class MyNode(BaseNode):
        """I hope this works"""

        pass

    # WHEN we serialize the node
    node_display_class = get_node_display_class(MyNode)
    data = node_display_class().serialize(WorkflowDisplayContext())

    # THEN the condition should be serialized correctly
    assert data["display_data"] == {
        "position": {"x": 0.0, "y": 0.0},
        "comment": {"expanded": True, "value": "I hope this works"},
    }


def test_serialize_node_label_with_pascal_case():
    """
    Tests that a node with PascalCase name serializes with proper title case label.
    """

    # GIVEN a node with a PascalCase name that includes common patterns
    class MyCustomNode(BaseNode):
        pass

    # WHEN we serialize the node
    node_display_class = get_node_display_class(MyCustomNode)
    data = node_display_class().serialize(WorkflowDisplayContext())

    # THEN the label should be converted to proper title case with spaces
    assert data["label"] == "My Custom Node"


def test_serialize_display_data_with_icon_and_color():
    """
    Tests that nodes with icon and color serialize display_data correctly.
    """

    # GIVEN a node with icon and color in display data
    class MyNode(BaseNode):
        pass

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        display_data = NodeDisplayData(
            position=NodeDisplayPosition(x=100, y=200), icon="vellum:icon:star", color="navy"
        )

    # WHEN we serialize the node
    data = MyNodeDisplay().serialize(WorkflowDisplayContext())

    # THEN the display_data should include icon and color
    assert data["display_data"] == {"position": {"x": 100, "y": 200}, "icon": "vellum:icon:star", "color": "navy"}


def test_serialize_display_data_with_various_icon_formats():
    """
    Tests that different icon formats are serialized correctly.
    """

    # GIVEN a node with a vellum icon format
    class MyNode(BaseNode):
        pass

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        display_data = NodeDisplayData(icon="vellum:icon:home")

    # WHEN we serialize the node
    data = MyNodeDisplay().serialize(WorkflowDisplayContext())

    # THEN the icon should be preserved as-is
    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:home"


def test_serialize_display_data_with_navy_color():
    """
    Tests that navy color values are serialized correctly.
    """

    # GIVEN a node with a navy color
    class MyNode(BaseNode):
        pass

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        display_data = NodeDisplayData(color="navy")

    # WHEN we serialize the node
    data = MyNodeDisplay().serialize(WorkflowDisplayContext())

    # THEN the color should be preserved as-is
    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["color"] == "navy"


def test_serialize_basenode_with_display_class():
    """Tests that BaseNode.Display class attributes serialize correctly."""

    class MyNode(BaseNode):
        class Display:
            icon = "vellum:icon:gear"
            color = "purple"

    node_display_class = get_node_display_class(MyNode)
    data = node_display_class().serialize(WorkflowDisplayContext())

    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:gear"
    assert display_data["color"] == "purple"


def test_serialize_explicit_display_data_overrides_display_class():
    """Tests that BaseNodeDisplay's explicit display_data takes precedence over Display class."""

    class MyNode(BaseNode):
        class Display:
            icon = "vellum:icon:check"
            color = "gold"

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        display_data = NodeDisplayData(
            position=NodeDisplayPosition(x=100, y=200),
            icon="vellum:icon:times",
            color="navy",
        )

    data = MyNodeDisplay().serialize(WorkflowDisplayContext())

    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:times"  # BaseNodeDisplay overrides
    assert display_data["color"] == "navy"  # BaseNodeDisplay overrides
    assert display_data["position"] == {"x": 100, "y": 200}


def test_serialize_display_class_used_as_fallback():
    """Tests that Display class attributes are used when BaseNodeDisplay doesn't specify them."""

    class MyNode(BaseNode):
        class Display:
            icon = "vellum:icon:star"
            color = "green"

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        display_data = NodeDisplayData(
            position=NodeDisplayPosition(x=50, y=75),
            # Not specifying icon or color - should fall back to Display class
        )

    data = MyNodeDisplay().serialize(WorkflowDisplayContext())

    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:star"  # Falls back to Display class
    assert display_data["color"] == "green"  # Falls back to Display class
    assert display_data["position"] == {"x": 50, "y": 75}  # From BaseNodeDisplay


def test_serialize_basenode_display_with_xyz():
    """Tests that BaseNode.Display x, y, z_index attributes serialize correctly."""

    # GIVEN a node with x, y, z_index in Display class
    class MyNode(BaseNode):
        class Display:
            x = 100.0
            y = 200.0
            z_index = 5

    # WHEN we serialize the node
    node_display_class = get_node_display_class(MyNode)
    data = node_display_class().serialize(WorkflowDisplayContext())

    # THEN the display_data should include position and z_index from Display class
    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["position"] == {"x": 100.0, "y": 200.0}
    assert display_data["z_index"] == 5


def test_serialize_basenode_display_with_partial_xy():
    """Tests that BaseNode.Display with only x or y still creates position."""

    # GIVEN a node with only x in Display class
    class MyNodeX(BaseNode):
        class Display:
            x = 150.0

    # WHEN we serialize the node
    node_display_class = get_node_display_class(MyNodeX)
    data = node_display_class().serialize(WorkflowDisplayContext())

    # THEN the display_data should include position with x and default y
    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["position"] == {"x": 150.0, "y": 0.0}


def test_serialize_explicit_display_data_overrides_display_class_xyz():
    """Tests that BaseNodeDisplay's explicit display_data takes precedence over Display class x, y, z_index."""

    # GIVEN a node with x, y, z_index in Display class
    class MyNode(BaseNode):
        class Display:
            x = 100.0
            y = 200.0
            z_index = 5

    # AND a BaseNodeDisplay with explicit display_data
    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        display_data = NodeDisplayData(
            position=NodeDisplayPosition(x=300, y=400),
            z_index=10,
        )

    # WHEN we serialize the node
    data = MyNodeDisplay().serialize(WorkflowDisplayContext())

    # THEN the display_data should use values from BaseNodeDisplay
    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["position"] == {"x": 300, "y": 400}  # BaseNodeDisplay overrides
    assert display_data["z_index"] == 10  # BaseNodeDisplay overrides


def test_serialize_display_class_xyz_used_as_fallback():
    """Tests that Display class x, y, z_index are used when BaseNodeDisplay doesn't specify them."""

    # GIVEN a node with x, y, z_index in Display class
    class MyNode(BaseNode):
        class Display:
            x = 50.0
            y = 75.0
            z_index = 3

    # AND a BaseNodeDisplay with only icon specified
    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        display_data = NodeDisplayData(
            icon="vellum:icon:star",
        )

    # WHEN we serialize the node
    data = MyNodeDisplay().serialize(WorkflowDisplayContext())

    # THEN the display_data should use x, y, z from Display class as fallback
    display_data = data["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["position"] == {"x": 50.0, "y": 75.0}  # Falls back to Display class
    assert display_data["z_index"] == 3  # Falls back to Display class
    assert display_data["icon"] == "vellum:icon:star"  # From BaseNodeDisplay
