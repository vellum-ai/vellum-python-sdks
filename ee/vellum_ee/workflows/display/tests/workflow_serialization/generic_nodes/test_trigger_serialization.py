from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.types.core import MergeBehavior


class Inputs(BaseInputs):
    input: str


class BasicGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


def test_serialize_node__basic(serialize_node):
    serialized_node = serialize_node(BasicGenericNode)
    assert not DeepDiff(
        {
            "id": "c2ed23f7-f6cb-4a56-a91c-2e5f9d8fda7f",
            "label": "BasicGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "BasicGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_trigger_serialization",
                ],
            },
            "trigger": {"id": "9d3a1b3d-4a38-4f2e-bbf1-dd8be152bce8", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "4fbf0fff-a42e-4410-852a-238b5059198e",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
        },
        serialized_node,
        ignore_order=True,
    )


class AwaitAnyGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY


def test_serialize_node__await_any(serialize_node):
    serialized_node = serialize_node(AwaitAnyGenericNode)
    assert not DeepDiff(
        {
            "id": "0ba67f76-aaff-4bd4-a20f-73a32ef5810d",
            "label": "AwaitAnyGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "AwaitAnyGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_trigger_serialization",
                ],
            },
            "trigger": {"id": "ffa72187-9a18-453f-ae55-b77aad332630", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "3e219c0a-e5f8-443a-ac78-1a458b189009",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
        },
        serialized_node,
        ignore_order=True,
    )


class AwaitAllGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ALL


def test_serialize_node__await_all(serialize_node):
    serialized_node = serialize_node(AwaitAllGenericNode)
    assert not DeepDiff(
        {
            "id": "09d06cd3-06ea-40cc-afd8-17ad88542271",
            "label": "AwaitAllGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "AwaitAllGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_trigger_serialization",
                ],
            },
            "trigger": {"id": "62074276-c817-476d-b59d-da523ae3f218", "merge_behavior": "AWAIT_ALL"},
            "ports": [
                {
                    "id": "9797e93f-9fe6-48b2-a48e-476abbd20e32",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
        },
        serialized_node,
        ignore_order=True,
    )
