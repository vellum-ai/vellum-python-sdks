from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.types.core import MergeBehavior


class Inputs(BaseInputs):
    input: str


def test_serialize_node__basic(serialize_node):
    class BasicGenericNode(BaseNode):
        pass

    serialized_node = serialize_node(BasicGenericNode)
    assert not DeepDiff(
        {
            "id": "8d7cbfe4-72ca-4367-a401-8d28723d2f00",
            "label": "test_serialize_node__basic.<locals>.BasicGenericNode",
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
            "trigger": {"id": "b95cca96-b570-42ac-ace8-51ca0f627881", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "8bec8d0c-113f-4110-afcb-4a6e566e7236",
                    "name": "default",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__await_any(serialize_node):
    class AwaitAnyGenericNode(BaseNode):
        class Trigger(BaseNode.Trigger):
            merge_behavior = MergeBehavior.AWAIT_ANY

    serialized_node = serialize_node(AwaitAnyGenericNode)
    assert not DeepDiff(
        {
            "id": "42e17f0e-8496-415f-9c72-f85250ba6f0b",
            "label": "test_serialize_node__await_any.<locals>.AwaitAnyGenericNode",
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
            "trigger": {"id": "c0db17e7-6766-4062-aaee-7404580d76e4", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "d9a84db7-8bd6-4a15-9e3c-c2e898c26d16",
                    "name": "default",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__await_all(serialize_node):
    class AwaitAllGenericNode(BaseNode):
        class Trigger(BaseNode.Trigger):
            merge_behavior = MergeBehavior.AWAIT_ALL

    serialized_node = serialize_node(AwaitAllGenericNode)
    assert not DeepDiff(
        {
            "id": "b3e1145a-5f41-456b-9382-6d0a1e828c2f",
            "label": "test_serialize_node__await_all.<locals>.AwaitAllGenericNode",
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
            "trigger": {"id": "1b22935e-0e79-485a-b274-a2f316c0983c", "merge_behavior": "AWAIT_ALL"},
            "ports": [
                {
                    "id": "fa73da35-0bf9-4f02-bf5b-0b0d1a6f1494",
                    "name": "default",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )
