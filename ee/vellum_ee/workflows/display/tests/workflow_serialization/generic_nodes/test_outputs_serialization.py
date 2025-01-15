from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode

from ee.vellum_ee.workflows.display.base import WorkflowInputsDisplay


class Inputs(BaseInputs):
    input: str


class WorkflowInputGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


def test_serialize_node__workflow_input(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=WorkflowInputGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )

    assert not DeepDiff(
        {
            "id": "ddfa947f-0830-476b-b07e-ac573968f9a7",
            "label": "WorkflowInputGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "WorkflowInputGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_outputs_serialization",
                ],
            },
            "trigger": {"id": "b1a5d749-bac0-4f11-8427-191febb2198e", "merge_behavior": "AWAIT_ANY"},
            "ports": [{"id": "f013bf3f-49f6-41cd-ac13-7439b71a304a", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [],
            "outputs": [
                {
                    "id": "2c4a85c0-b017-4cea-a261-e8e8498570c9",
                    "name": "output",
                    "type": "STRING",
                    "value": {
                        "type": "WORKFLOW_INPUT",
                        "input_variable_id": str(input_id),
                    },
                }
            ],
        },
        serialized_node,
        ignore_order=True,
    )
