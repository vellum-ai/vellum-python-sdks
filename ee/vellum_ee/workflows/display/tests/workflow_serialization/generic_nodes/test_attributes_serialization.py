from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode

from ee.vellum_ee.workflows.display.base import WorkflowInputsDisplay


class Inputs(BaseInputs):
    input: str


class ConstantValueGenericNode(BaseNode):
    attr: str = "hello"

    class Outputs(BaseNode.Outputs):
        output = Inputs.input


def test_serialize_node__constant_value(serialize_node):
    serialized_node = serialize_node(ConstantValueGenericNode)
    assert not DeepDiff(
        {
            "id": "be892bc8-e4de-47ef-ab89-dc9d869af1fe",
            "label": "ConstantValueGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "ConstantValueGenericNode",
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
            "trigger": {"id": "279e8228-9b82-43a3-8c31-affc036e3a0b", "merge_behavior": "AWAIT_ANY"},
            "ports": [{"id": "e6cf13b0-5590-421c-84f2-5a0b169677e1", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "4cbbfd98-9ab6-41a8-bf4e-ae65f0eafe47",
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
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


class WorkflowInputGenericNode(BaseNode):
    attr: str = Inputs.input

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
                    "test_attributes_serialization",
                ],
            },
            "trigger": {"id": "b1a5d749-bac0-4f11-8427-191febb2198e", "merge_behavior": "AWAIT_ANY"},
            "ports": [{"id": "f013bf3f-49f6-41cd-ac13-7439b71a304a", "type": "DEFAULT", "name": "default"}],
            "adornments": None,
            "attributes": [
                {
                    "id": "56d44313-cfdd-4d75-9b19-0beb94e59c4e",
                    "name": "attr",
                    "value": {
                        "type": "WORKFLOW_INPUT",
                        "input_variable_id": str(input_id),
                    },
                }
            ],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )
