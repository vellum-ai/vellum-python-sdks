import pytest

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode


class Inputs(BaseInputs):
    input: str


class BasicGenericNode(BaseNode):
    attr: str = "hello"

    class Outputs(BaseNode.Outputs):
        output = Inputs.input


@pytest.mark.skip(reason="not implemented")
def test_serialize_node__try(serialize_node):
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
                    "test_attributes_serialization",
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
            "attributes": [
                {
                    "id": "e3c8b6e4-4b7d-4e3c-8a5c-6e5f4e3c8b6e",
                    "name": "attr",
                    "value": {
                        "type": "CONSTANT_VALUE",
                        "value": {
                            "type": "STRING",
                            "value": "hello",
                        },
                    },
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )
