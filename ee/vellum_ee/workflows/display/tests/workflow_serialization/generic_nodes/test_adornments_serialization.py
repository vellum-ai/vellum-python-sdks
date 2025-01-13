import pytest

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.map_node.node import MapNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    foo: str


class State(BaseState):
    bar: str


@MapNode.wrap(items=[1, 2, 3])
class MapGenericNode(BaseNode):
    item = MapNode.SubworkflowInputs.item
    foo = Inputs.foo
    bar = State.bar

    class Outputs(BaseOutputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value=f"{self.foo} {self.bar} {self.item}")


@pytest.mark.skip(reason="not implemented")
def test_serialize_node__try(serialize_node):
    serialized_node = serialize_node(MapGenericNode)
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
                    "test_adornments_serialization",
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
