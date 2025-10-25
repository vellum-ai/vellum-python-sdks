from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_templating_node.workflow_with_json_input import BasicTemplatingNodeWorkflowWithJson


def test_serialize_workflow():
    # GIVEN a Workflow that uses a vellum templating node",

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicTemplatingNodeWorkflowWithJson)

    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1
    assert input_variables == [
        {
            "id": "f4435f88-703f-40e5-9197-d39b0e43ab72",
            "key": "info",
            "type": "JSON",
            "default": None,
            "required": True,
            "extensions": {"color": None},
        }
    ]

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert not DeepDiff(
        [{"id": "62ec9b08-6437-4f8d-bc20-983d317bc348", "key": "result", "type": "JSON"}],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["edges"]) == 2
    assert len(workflow_raw_data["nodes"]) == 3

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "09579c0a-acbf-4e04-8724-2230a8aa6534",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "34069190-0942-4e0c-8700-b33b9dea4ea0"},
        "display_data": {"position": {"x": 0.0, "y": -50.0}},
        "base": None,
        "definition": None,
    }

    templating_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "28ac8611-a755-4d8a-a5c3-520ddd119cf8",
            "type": "TEMPLATING",
            "inputs": [
                {
                    "id": "7ceb3528-49c6-4f90-b3ef-92b1921a1b7d",
                    "key": "template",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "The meaning of {{ info }} is not known"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "f46b5986-74f1-4ad4-b4d1-b8d2df6bc86f",
                    "key": "info",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "f4435f88-703f-40e5-9197-d39b0e43ab72"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
            ],
            "data": {
                "label": "Example Templating Node",
                "output_id": "076becd5-f282-40c5-9917-61099e114298",
                "error_output_id": None,
                "source_handle_id": "90a2ea33-b08d-46ec-8d9e-612592764268",
                "target_handle_id": "a215a440-cbd9-48ae-a831-be8fa78530a6",
                "template_node_input_id": "7ceb3528-49c6-4f90-b3ef-92b1921a1b7d",
                "output_type": "JSON",
            },
            "display_data": {"position": {"x": 200.0, "y": -50.0}},
            "base": {
                "name": "TemplatingNode",
                "module": ["vellum", "workflows", "nodes", "core", "templating_node", "node"],
            },
            "definition": {
                "name": "ExampleTemplatingNode",
                "module": ["tests", "workflows", "basic_templating_node", "workflow_with_json_input"],
            },
            "trigger": {
                "id": "a215a440-cbd9-48ae-a831-be8fa78530a6",
                "merge_behavior": "AWAIT_ATTRIBUTES",
            },
            "ports": [{"id": "90a2ea33-b08d-46ec-8d9e-612592764268", "name": "default", "type": "DEFAULT"}],
        },
        templating_node,
    )

    final_output_node = workflow_raw_data["nodes"][-1]
    assert not DeepDiff(
        {
            "id": "9f75228b-1d5b-4c30-a581-6087e6a1b738",
            "type": "TERMINAL",
            "data": {
                "label": "Final Output",
                "name": "result",
                "target_handle_id": "16ba108e-61a8-4338-8a5b-4f1278d7fd7b",
                "output_id": "62ec9b08-6437-4f8d-bc20-983d317bc348",
                "output_type": "JSON",
                "node_input_id": "da51bb91-227c-481c-84d7-69c64322b485",
            },
            "inputs": [
                {
                    "id": "da51bb91-227c-481c-84d7-69c64322b485",
                    "key": "node_input",
                    "value": {
                        "rules": [
                            {
                                "type": "NODE_OUTPUT",
                                "data": {
                                    "node_id": "28ac8611-a755-4d8a-a5c3-520ddd119cf8",
                                    "output_id": "076becd5-f282-40c5-9917-61099e114298",
                                },
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "display_data": {"position": {"x": 400.0, "y": -50.0}},
            "base": {
                "name": "FinalOutputNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
            },
            "definition": None,
        },
        final_output_node,
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "7f26b32f-defb-4a2a-8656-c719fc9996a8",
                "source_node_id": "09579c0a-acbf-4e04-8724-2230a8aa6534",
                "source_handle_id": "34069190-0942-4e0c-8700-b33b9dea4ea0",
                "target_node_id": "28ac8611-a755-4d8a-a5c3-520ddd119cf8",
                "target_handle_id": "a215a440-cbd9-48ae-a831-be8fa78530a6",
                "type": "DEFAULT",
            },
            {
                "id": "00cbff5c-5cce-4ef4-81b2-1a11d9b42597",
                "source_node_id": "28ac8611-a755-4d8a-a5c3-520ddd119cf8",
                "source_handle_id": "90a2ea33-b08d-46ec-8d9e-612592764268",
                "target_node_id": "9f75228b-1d5b-4c30-a581-6087e6a1b738",
                "target_handle_id": "16ba108e-61a8-4338-8a5b-4f1278d7fd7b",
                "type": "DEFAULT",
            },
        ],
        serialized_edges,
        ignore_order=True,
    )

    # AND the display data should be what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {
        "viewport": {
            "x": 0.0,
            "y": 0.0,
            "zoom": 1.0,
        }
    }

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicTemplatingNodeWorkflowWithJson",
        "module": ["tests", "workflows", "basic_templating_node", "workflow_with_json_input"],
    }
