import pytest
from uuid import UUID

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.constant import ConstantValueReference
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import WorkflowDisplayContext


@pytest.fixture
def node_with_implicit_properties():
    class MyNode(BaseNode):
        pass

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        pass

    expected_id = UUID("ace7f746-4fe6-45c7-8207-fc8a4d0c7f6f")

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
            "id": "7de6ea94-7f6c-475e-8f38-ec8ac317fd19",
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
        "comment": {"value": "I hope this works"},
    }
