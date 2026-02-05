from typing import List

from vellum import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.set_state_node import SetStateNode
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_chat_message_dict_reference_with_definition():
    """Test that ChatMessage dictionary references are serialized with definition field."""

    class State(BaseState):
        chat_history: List[ChatMessage] = []

    class Inputs(BaseInputs):
        message: str

    class StoreUserMessage(SetStateNode[State]):
        operations = {
            "chat_history": State.chat_history
            + ChatMessage(
                text=Inputs.message,
                role="USER",
            ),
        }

    class TestWorkflow(BaseWorkflow[Inputs, State]):
        graph = StoreUserMessage

        class Outputs(BaseWorkflow.Outputs):
            chat_history = State.chat_history

    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow = workflow_display.serialize()

    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)

    set_state_node = next(
        node
        for node in nodes
        if isinstance(node, dict) and node.get("type") == "GENERIC" and node.get("label") == "Store User Message"
    )

    assert isinstance(set_state_node, dict)
    assert "attributes" in set_state_node
    attributes = set_state_node["attributes"]
    assert isinstance(attributes, list)

    operations_attribute = next(
        attribute for attribute in attributes if isinstance(attribute, dict) and attribute.get("name") == "operations"
    )
    assert isinstance(operations_attribute, dict)

    assert operations_attribute == {
        "id": "b1a79be0-9b4f-4236-aaba-a0ebd56e2079",
        "name": "operations",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "160c6ef1-30b4-40ff-8cad-88d73bc6ea54",
                    "key": "chat_history",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "WORKFLOW_STATE", "state_variable_id": "fff74a8e-752e-4088-9d3e-493e9162bda5"},
                        "operator": "+",
                        "rhs": {
                            "type": "DICTIONARY_REFERENCE",
                            "entries": [
                                {
                                    "id": "f50f80a5-3b36-4077-a90f-c13b38fd7919",
                                    "key": "text",
                                    "value": {
                                        "type": "WORKFLOW_INPUT",
                                        "input_variable_id": "cb4bd466-58e9-4ecd-a2b3-22ce280a0422",
                                    },
                                },
                                {
                                    "id": "2047e859-8c1a-42b9-b4d4-b6d6fc7b33b2",
                                    "key": "role",
                                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "USER"}},
                                },
                                {
                                    "id": "ca0c0a31-e903-4908-998d-10916e287d77",
                                    "key": "content",
                                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                                },
                                {
                                    "id": "78565b95-23a0-4be4-a9ce-89893a60f458",
                                    "key": "source",
                                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                                },
                                {
                                    "id": "e39552e3-8bf4-4272-85d3-e4cab71155ac",
                                    "key": "metadata",
                                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                                },
                            ],
                            "definition": {
                                "name": "ChatMessage",
                                "module": ["vellum", "client", "types", "chat_message"],
                            },
                        },
                    },
                }
            ],
        },
    }


def test_serialize_chat_message_trigger_with_message_parameter():
    """Test that ChatMessageTrigger with message parameter serializes correctly in dataset."""
    # GIVEN a workflow module with a ChatMessageTrigger that has a message parameter
    module_path = "tests.workflows.test_chat_message_trigger_serialization"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module_path)

    # THEN the dataset should contain the trigger's message in inputs
    assert result.dataset is not None
    assert isinstance(result.dataset, list)
    assert len(result.dataset) == 1

    # AND the message should be serialized in the inputs as array format
    dataset_row = result.dataset[0]
    assert dataset_row["label"] == "New conversation"
    assert "inputs" in dataset_row
    assert dataset_row["inputs"]["message"] == [{"type": "STRING", "value": "I want to tweet about AI agents"}]
