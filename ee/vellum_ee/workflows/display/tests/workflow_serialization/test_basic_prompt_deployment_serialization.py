from datetime import datetime
from uuid import uuid4

from deepdiff import DeepDiff

from vellum import DeploymentRead
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_text_prompt_deployment.workflow import BasicTextPromptDeployment
from tests.workflows.basic_text_prompt_deployment.workflow_with_prompt_deployment_json_reference import (
    WorkflowWithPromptDeploymentJsonReferenceWorkflow,
)


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
    workflow_display = get_workflow_display(workflow_class=BasicTextPromptDeployment)
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
                "id": "947d7ead-0fad-4e5f-aa3a-d06029ac94bc",
                "key": "city",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "52995b50-84c9-465f-8a4b-a4ee2a92e388"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "3deebdd7-2900-4d8c-93f2-e5b90649ac42",
                "key": "date",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "aa3ca842-250c-4a3f-853f-23928c28d0f8"},
                        }
                    ],
                    "combinator": "OR",
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
            "ml_model_fallbacks": ["gpt-4o", "gemini-1.5-pro"],
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "name": "PromptDeploymentNode",
            "module": ["vellum", "workflows", "nodes", "displayable", "prompt_deployment_node", "node"],
        },
        "definition": {
            "name": "ExamplePromptDeploymentNode",
            "module": ["tests", "workflows", "basic_text_prompt_deployment", "workflow"],
        },
        "ports": [{"id": "2f26c7e0-283d-4f04-b639-adebb56bc679", "name": "default", "type": "DEFAULT"}],
        "outputs": [
            {"id": "180355a8-e67c-4ce6-9ac3-e5dbb75a6629", "name": "json", "type": "JSON", "value": None},
            {"id": "4d38b850-79e3-4b85-9158-a41d0c535410", "name": "text", "type": "STRING", "value": None},
            {"id": "0cf47d33-6d5f-466f-b826-e814f1d0348b", "name": "results", "type": "ARRAY", "value": None},
        ],
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
                "id": "78aeb65b-3491-4d2a-8c47-401d4cb3d560",
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
            "node_input_id": "78aeb65b-3491-4d2a-8c47-401d4cb3d560",
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


def test_serialize_workflow_with_prompt_and_templating(vellum_client):
    # GIVEN a Workflow with stubbed out API calls
    deployment = DeploymentRead(
        id=str(uuid4()),
        created=datetime.now(),
        label="JSON Prompt Deployment",
        name="json_prompt_deployment",
        last_deployed_on=datetime.now(),
        input_variables=[],
        active_model_version_ids=[],
        last_deployed_history_item_id=str(uuid4()),
    )
    vellum_client.deployments.retrieve.return_value = deployment

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=WorkflowWithPromptDeploymentJsonReferenceWorkflow)
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
    assert len(input_variables) == 2
    assert not DeepDiff(
        [
            {
                "id": "ad577aca-0797-4deb-a484-574ef1a1f0c7",
                "key": "city",
                "type": "STRING",
                "default": None,
                "required": True,
                "extensions": {"color": None},
            },
            {
                "id": "066124c4-42bd-4764-aa75-6f230dbbed4a",
                "key": "date",
                "type": "STRING",
                "default": None,
                "required": True,
                "extensions": {"color": None},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables == [{"id": "a7e4b449-5879-4d0c-8f00-d5d4985eb65c", "key": "text", "type": "STRING"}]

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["edges"]) == 3
    assert len(workflow_raw_data["nodes"]) == 4

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "32c7f398-277c-456b-9279-aa1f867fb637",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "cc0f4028-1039-4063-971d-7dacbb01b379"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
    }

    prompt_node = workflow_raw_data["nodes"][1]
    assert prompt_node == {
        "id": "56c74024-19a3-4c0d-a5f5-23e1e9f11b21",
        "type": "PROMPT",
        "inputs": [
            {
                "id": "947d7ead-0fad-4e5f-aa3a-d06029ac94bc",
                "key": "city",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "ad577aca-0797-4deb-a484-574ef1a1f0c7"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "3deebdd7-2900-4d8c-93f2-e5b90649ac42",
                "key": "date",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "066124c4-42bd-4764-aa75-6f230dbbed4a"},
                        }
                    ],
                    "combinator": "OR",
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
            "ml_model_fallbacks": None,
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "name": "PromptDeploymentNode",
            "module": ["vellum", "workflows", "nodes", "displayable", "prompt_deployment_node", "node"],
        },
        "definition": {
            "name": "ExamplePromptDeploymentNode",
            "module": [
                "tests",
                "workflows",
                "basic_text_prompt_deployment",
                "workflow_with_prompt_deployment_json_reference",
            ],
        },
        "ports": [{"id": "2f26c7e0-283d-4f04-b639-adebb56bc679", "name": "default", "type": "DEFAULT"}],
        "outputs": [
            {"id": "180355a8-e67c-4ce6-9ac3-e5dbb75a6629", "name": "json", "type": "JSON", "value": None},
            {"id": "4d38b850-79e3-4b85-9158-a41d0c535410", "name": "text", "type": "STRING", "value": None},
            {"id": "0cf47d33-6d5f-466f-b826-e814f1d0348b", "name": "results", "type": "ARRAY", "value": None},
        ],
    }

    templating_node = workflow_raw_data["nodes"][2]
    assert templating_node == {
        "id": "51cbe21d-0232-4362-bc54-5bc283297aa6",
        "type": "TEMPLATING",
        "inputs": [
            {
                "id": "7c775379-d589-4d79-b876-dcd224d72966",
                "key": "template",
                "value": {
                    "rules": [
                        {
                            "type": "CONSTANT_VALUE",
                            "data": {
                                "type": "STRING",
                                "value": "The weather in {{ city }} on {{ date }} is {{ weather }}.",
                            },
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "dec1317a-6900-4858-a5fb-c849254b2c91",
                "key": "city",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "ad577aca-0797-4deb-a484-574ef1a1f0c7"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "4cc5b9f1-075d-45fd-a978-f530c29c5682",
                "key": "date",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "066124c4-42bd-4764-aa75-6f230dbbed4a"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "77b352e0-1b77-4d48-9f6f-04ce17fe7286",
                "key": "weather",
                "value": {
                    "rules": [
                        {
                            "type": "NODE_OUTPUT",
                            "data": {
                                "node_id": "56c74024-19a3-4c0d-a5f5-23e1e9f11b21",
                                "output_id": "180355a8-e67c-4ce6-9ac3-e5dbb75a6629",
                            },
                        }
                    ],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Example Templating Node",
            "output_id": "6834cae4-8173-4fa6-88f7-bc09d335bdd1",
            "error_output_id": None,
            "source_handle_id": "39317827-df43-4f5a-bfbc-20bffc839748",
            "target_handle_id": "58427684-3848-498a-8299-c6b0fc70265d",
            "template_node_input_id": "7c775379-d589-4d79-b876-dcd224d72966",
            "output_type": "STRING",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "name": "TemplatingNode",
            "module": ["vellum", "workflows", "nodes", "core", "templating_node", "node"],
        },
        "definition": {
            "name": "ExampleTemplatingNode",
            "module": [
                "tests",
                "workflows",
                "basic_text_prompt_deployment",
                "workflow_with_prompt_deployment_json_reference",
            ],
        },
        "ports": [{"id": "39317827-df43-4f5a-bfbc-20bffc839748", "name": "default", "type": "DEFAULT"}],
    }

    final_output_node = workflow_raw_data["nodes"][3]
    assert final_output_node == {
        "id": "53de824d-a41d-4294-b511-c969932b05af",
        "type": "TERMINAL",
        "data": {
            "label": "Final Output",
            "name": "text",
            "target_handle_id": "fee3d395-38c3-485f-ab61-1a0fdf71c4ce",
            "output_id": "a7e4b449-5879-4d0c-8f00-d5d4985eb65c",
            "output_type": "STRING",
            "node_input_id": "cf380f81-c5ee-4bc9-8e26-ecf1307733a9",
        },
        "inputs": [
            {
                "id": "cf380f81-c5ee-4bc9-8e26-ecf1307733a9",
                "key": "node_input",
                "value": {
                    "rules": [
                        {
                            "type": "NODE_OUTPUT",
                            "data": {
                                "node_id": "51cbe21d-0232-4362-bc54-5bc283297aa6",
                                "output_id": "6834cae4-8173-4fa6-88f7-bc09d335bdd1",
                            },
                        }
                    ],
                    "combinator": "OR",
                },
            }
        ],
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "name": "FinalOutputNode",
            "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
        },
        "definition": None,
    }

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert serialized_edges == [
        {
            "id": "2c49ffa6-7b9a-49a0-a932-009534556480",
            "source_node_id": "32c7f398-277c-456b-9279-aa1f867fb637",
            "source_handle_id": "cc0f4028-1039-4063-971d-7dacbb01b379",
            "target_node_id": "56c74024-19a3-4c0d-a5f5-23e1e9f11b21",
            "target_handle_id": "b7605c48-0937-4ecc-914e-0d1058130e65",
            "type": "DEFAULT",
        },
        {
            "id": "a46909ec-9572-43c6-a134-0bd7e2c09f99",
            "source_node_id": "56c74024-19a3-4c0d-a5f5-23e1e9f11b21",
            "source_handle_id": "2f26c7e0-283d-4f04-b639-adebb56bc679",
            "target_node_id": "51cbe21d-0232-4362-bc54-5bc283297aa6",
            "target_handle_id": "58427684-3848-498a-8299-c6b0fc70265d",
            "type": "DEFAULT",
        },
        {
            "id": "1f720900-e5e1-49b7-9910-6ede79f6afd2",
            "source_node_id": "51cbe21d-0232-4362-bc54-5bc283297aa6",
            "source_handle_id": "39317827-df43-4f5a-bfbc-20bffc839748",
            "target_node_id": "53de824d-a41d-4294-b511-c969932b05af",
            "target_handle_id": "fee3d395-38c3-485f-ab61-1a0fdf71c4ce",
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
        "name": "WorkflowWithPromptDeploymentJsonReferenceWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_text_prompt_deployment",
            "workflow_with_prompt_deployment_json_reference",
        ],
    }
