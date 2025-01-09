from datetime import datetime
from uuid import uuid4

from deepdiff import DeepDiff

from vellum import DeploymentRead
from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_text_prompt_deployment.workflow import BasicTextPromptDeployment


def test_serialize_workflow(vellum_client):
    # GIVEN a Workflow with stubbed out API calls
    deployment = DeploymentRead(
        id=str(uuid4()),
        created=datetime.now(),
        label="Example Prompt Deployment",
        name="example_prompt_deployment",
        last_deployed_on=datetime.now(),
        input_variables=[],
        active_model_version_ids=[],
        last_deployed_history_item_id=str(uuid4()),
    )
    vellum_client.deployments.retrieve.return_value = deployment

    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=BasicTextPromptDeployment
    )
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 2
    assert not DeepDiff(
        [
            {
                "id": "52995b50-84c9-465f-8a4b-a4ee2a92e388",
                "key": "city",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
            },
            {
                "id": "aa3ca842-250c-4a3f-853f-23928c28d0f8",
                "key": "date",
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
    assert output_variables == [
        {
            "id": "a609ab19-db1b-4cd0-bdb0-aee5ed31dc28",
            "key": "text",
            "type": "STRING",
        }
    ]

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert workflow_raw_data.keys() == {"edges", "nodes", "display_data", "definition"}
    assert len(workflow_raw_data["edges"]) == 2
    assert len(workflow_raw_data["nodes"]) == 3

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "d680afbd-de64-4cf6-aa50-912686c48c64",
        "type": "ENTRYPOINT",
        "inputs": [],
        "base": None,
        "definition": None,
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "7065a943-1cab-4afd-9690-e678c5b74a2f",
        },
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
        },
    }

    prompt_node = workflow_raw_data["nodes"][1]
    assert prompt_node == {
        "id": "56c74024-19a3-4c0d-a5f5-23e1e9f11b21",
        "type": "PROMPT",
        "inputs": [
            {
                "id": "509cf3d4-db72-483e-897a-0f7f20e70d03",
                "key": "city",
                "value": {
                    "combinator": "OR",
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {
                                "input_variable_id": "52995b50-84c9-465f-8a4b-a4ee2a92e388",
                            },
                        },
                    ],
                },
            },
            {
                "id": "7d6ec5ac-c582-4153-bd8a-b8794c367420",
                "key": "date",
                "value": {
                    "combinator": "OR",
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {
                                "input_variable_id": "aa3ca842-250c-4a3f-853f-23928c28d0f8",
                            },
                        },
                    ],
                },
            },
        ],
        "data": {
            "label": "Example Prompt Deployment Node",
            "output_id": "4d38b850-79e3-4b85-9158-a41d0c535410",
            "error_output_id": None,
            "array_output_id": "0cf47d33-6d5f-466f-b826-e814f1d0348b",
            "source_handle_id": "2f26c7e0-283d-4f04-b639-adebb56bc679",
            "target_handle_id": "b7605c48-0937-4ecc-914e-0d1058130e65",
            "variant": "DEPLOYMENT",
            "prompt_deployment_id": deployment.id,
            "release_tag": "LATEST",
        },
        "display_data": {
            "position": {
                "x": 0.0,
                "y": 0.0,
            },
        },
        "base": {
            "module": ["vellum", "workflows", "nodes", "displayable", "prompt_deployment_node", "node"],
            "name": "PromptDeploymentNode",
        },
        "definition": {
            "module": ["tests", "workflows", "basic_text_prompt_deployment", "workflow"],
            "name": "ExamplePromptDeploymentNode",
        },
    }

    final_output_node = workflow_raw_data["nodes"][2]
    assert final_output_node == {
        "id": "64ff72c7-8ffc-4e1f-b7a7-e7cd0697f576",
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
        "inputs": [
            {
                "id": "5f0fdd0f-63fe-4437-bc1b-cd6a84bb84c5",
                "key": "node_input",
                "value": {
                    "combinator": "OR",
                    "rules": [
                        {
                            "data": {
                                "node_id": "56c74024-19a3-4c0d-a5f5-23e1e9f11b21",
                                "output_id": "4d38b850-79e3-4b85-9158-a41d0c535410",
                            },
                            "type": "NODE_OUTPUT",
                        }
                    ],
                },
            }
        ],
        "data": {
            "label": "Final Output",
            "name": "text",
            "node_input_id": "5f0fdd0f-63fe-4437-bc1b-cd6a84bb84c5",
            "output_id": "a609ab19-db1b-4cd0-bdb0-aee5ed31dc28",
            "output_type": "STRING",
            "target_handle_id": "dced939a-9122-4290-8482-7daa9525dad6",
        },
        "display_data": {
            "position": {
                "x": 0.0,
                "y": 0.0,
            },
        },
    }

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert serialized_edges == [
        {
            "id": "8961d02b-074e-45ab-9f77-4e94606a4344",
            "source_handle_id": "7065a943-1cab-4afd-9690-e678c5b74a2f",
            "source_node_id": "d680afbd-de64-4cf6-aa50-912686c48c64",
            "target_handle_id": "b7605c48-0937-4ecc-914e-0d1058130e65",
            "target_node_id": "56c74024-19a3-4c0d-a5f5-23e1e9f11b21",
            "type": "DEFAULT",
        },
        {
            "id": "c2cbf6ef-8582-45c8-a643-fc6ae8fe482f",
            "source_handle_id": "2f26c7e0-283d-4f04-b639-adebb56bc679",
            "source_node_id": "56c74024-19a3-4c0d-a5f5-23e1e9f11b21",
            "target_handle_id": "dced939a-9122-4290-8482-7daa9525dad6",
            "target_node_id": "64ff72c7-8ffc-4e1f-b7a7-e7cd0697f576",
            "type": "DEFAULT",
        },
    ]

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
        "name": "BasicTextPromptDeployment",
        "module": [
            "tests",
            "workflows",
            "basic_text_prompt_deployment",
            "workflow",
        ],
    }
