from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_guardrail_node.workflow import BasicGuardrailNodeWorkflow


def test_serialize_workflow():
    # GIVEN a workflow that uses a guardrail node
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=BasicGuardrailNodeWorkflow
    )

    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the workflow
    assert serialized_workflow.keys() == {"workflow_raw_data", "input_variables", "state_variables", "output_variables"}

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 2
    assert not DeepDiff(
        [
            {
                "id": "eb1b1913-9fb8-4b8c-8901-09d9b9edc1c3",
                "key": "actual",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
            },
            {
                "id": "545ff95e-e86f-4d06-a991-602781e72605",
                "key": "expected",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables == [{"id": "2abd2b3b-c301-4834-a43f-5db3604f8422", "key": "score", "type": "NUMBER"}]

    # AND its raw data is what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert workflow_raw_data.keys() == {"nodes", "edges", "display_data", "definition"}
    assert len(workflow_raw_data["nodes"]) == 3
    assert len(workflow_raw_data["edges"]) == 2

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "54c5c7d0-ab86-4ae9-b0b8-ea9ca7b87c14",
        "type": "ENTRYPOINT",
        "base": None,
        "definition": None,
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "41840690-8d85-486e-a864-b0661ccf0f2e"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
    }

    guardrail_node = workflow_raw_data["nodes"][1]
    assert guardrail_node == {
        "id": "5573f078-cced-48f3-bafd-782d48e260c7",
        "type": "METRIC",
        "inputs": [
            {
                "id": "e5e9757e-27db-4200-a650-2f7bb2cd61f5",
                "key": "expected",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "545ff95e-e86f-4d06-a991-602781e72605"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "f5cd9336-e8e9-429e-b7bc-785402e31bfb",
                "key": "actual",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "eb1b1913-9fb8-4b8c-8901-09d9b9edc1c3"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Example Guardrail Node",
            "source_handle_id": "0ed87407-697e-4ae9-ab9b-6c5cc2e57cf7",
            "target_handle_id": "ce5b85b1-eded-46dd-b4b7-020afcdc67ab",
            "error_output_id": None,
            "metric_definition_id": "example_metric_definition",
            "release_tag": "LATEST",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "module": ["vellum", "workflows", "nodes", "displayable", "guardrail_node", "node"],
            "name": "GuardrailNode",
        },
        "definition": {
            "module": ["tests", "workflows", "basic_guardrail_node", "workflow"],
            "name": "ExampleGuardrailNode",
        },
    }

    final_output_node = workflow_raw_data["nodes"][2]
    assert final_output_node == {
        "id": "cbc7197e-67c9-4af5-b781-879c8fd3e4c9",
        "type": "TERMINAL",
        "base": {
            "module": [
                "vellum",
                "workflows",
                "nodes",
                "displayable",
                "final_output_node",
                "node",
            ],
            "name": "FinalOutputNode",
        },
        "definition": None,
        "data": {
            "label": "Final Output",
            "name": "score",
            "target_handle_id": "001b97f6-2bc8-4d1e-9572-028dcf17df4e",
            "output_id": "2abd2b3b-c301-4834-a43f-5db3604f8422",
            "output_type": "NUMBER",
            "node_input_id": "6321442a-0d0d-4e25-965d-c24ff24712c5",
        },
        "inputs": [
            {
                "id": "6321442a-0d0d-4e25-965d-c24ff24712c5",
                "key": "node_input",
                "value": {
                    "rules": [
                        {
                            "type": "NODE_OUTPUT",
                            "data": {
                                "node_id": "5573f078-cced-48f3-bafd-782d48e260c7",
                                "output_id": "0cce9413-687e-43e9-af04-a488334688fa",
                            },
                        }
                    ],
                    "combinator": "OR",
                },
            }
        ],
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
    }

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert serialized_edges == [
        {
            "id": "7bab1cc9-eedd-4e76-8bc1-0437b842c3bd",
            "source_node_id": "54c5c7d0-ab86-4ae9-b0b8-ea9ca7b87c14",
            "source_handle_id": "41840690-8d85-486e-a864-b0661ccf0f2e",
            "target_node_id": "5573f078-cced-48f3-bafd-782d48e260c7",
            "target_handle_id": "ce5b85b1-eded-46dd-b4b7-020afcdc67ab",
            "type": "DEFAULT",
        },
        {
            "id": "5c456a17-a92b-4dad-9569-306043707c9f",
            "source_node_id": "5573f078-cced-48f3-bafd-782d48e260c7",
            "source_handle_id": "0ed87407-697e-4ae9-ab9b-6c5cc2e57cf7",
            "target_node_id": "cbc7197e-67c9-4af5-b781-879c8fd3e4c9",
            "target_handle_id": "001b97f6-2bc8-4d1e-9572-028dcf17df4e",
            "type": "DEFAULT",
        },
    ]

    # AND the display data is what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}}

    # AND the definition is what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicGuardrailNodeWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_guardrail_node",
            "workflow",
        ],
    }
