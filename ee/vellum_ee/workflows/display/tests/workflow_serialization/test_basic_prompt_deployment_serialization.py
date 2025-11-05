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
            "position": {"x": 0.0, "y": -50.0},
        },
    }

    prompt_node = workflow_raw_data["nodes"][1]
    assert prompt_node == {
        "id": "a114abf2-cb76-49b5-8001-6c8df56d39ff",
        "type": "PROMPT",
        "inputs": [
            {
                "id": "c58d2244-a52e-4edb-84c5-efc334dea6f9",
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
                "id": "d00707fb-b584-40bc-aecd-db11490bea3e",
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
            "output_id": "f07b3521-4ba1-4a3c-8629-3a269406f519",
            "error_output_id": None,
            "array_output_id": "14d71e78-94a5-4c46-bad8-bec827a4f1e4",
            "source_handle_id": "6699f465-dc6c-4fa7-8038-7ff49419b953",
            "target_handle_id": "1407e51f-cb29-4a86-beeb-cc1870dc5525",
            "variant": "DEPLOYMENT",
            "prompt_deployment_id": deployment.id,
            "release_tag": "LATEST",
            "ml_model_fallbacks": ["gpt-4o", "gemini-1.5-pro"],
        },
        "display_data": {"position": {"x": 200.0, "y": -50.0}},
        "base": {
            "name": "PromptDeploymentNode",
            "module": ["vellum", "workflows", "nodes", "displayable", "prompt_deployment_node", "node"],
        },
        "definition": {
            "name": "ExamplePromptDeploymentNode",
            "module": ["tests", "workflows", "basic_text_prompt_deployment", "workflow"],
        },
        "trigger": {
            "id": "1407e51f-cb29-4a86-beeb-cc1870dc5525",
            "merge_behavior": "AWAIT_ANY",
        },
        "ports": [{"id": "6699f465-dc6c-4fa7-8038-7ff49419b953", "name": "default", "type": "DEFAULT"}],
        "outputs": [
            {"id": "66687de8-3e00-4290-9177-54be727fef44", "name": "json", "type": "JSON", "value": None},
            {"id": "f07b3521-4ba1-4a3c-8629-3a269406f519", "name": "text", "type": "STRING", "value": None},
            {"id": "14d71e78-94a5-4c46-bad8-bec827a4f1e4", "name": "results", "type": "ARRAY", "value": None},
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
                                "node_id": "a114abf2-cb76-49b5-8001-6c8df56d39ff",
                                "output_id": "f07b3521-4ba1-4a3c-8629-3a269406f519",
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
                "x": 400.0,
                "y": -50.0,
            },
        },
    }

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert serialized_edges == [
        {
            "id": "89a6042d-2bfd-4512-9f75-bf11db3c493c",
            "source_handle_id": "7065a943-1cab-4afd-9690-e678c5b74a2f",
            "source_node_id": "d680afbd-de64-4cf6-aa50-912686c48c64",
            "target_handle_id": "1407e51f-cb29-4a86-beeb-cc1870dc5525",
            "target_node_id": "a114abf2-cb76-49b5-8001-6c8df56d39ff",
            "type": "DEFAULT",
        },
        {
            "id": "c2cbf6ef-8582-45c8-a643-fc6ae8fe482f",
            "source_handle_id": "6699f465-dc6c-4fa7-8038-7ff49419b953",
            "source_node_id": "a114abf2-cb76-49b5-8001-6c8df56d39ff",
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
        "display_data": {"position": {"x": 0.0, "y": -50.0}},
        "base": None,
        "definition": None,
    }

    prompt_node = workflow_raw_data["nodes"][1]
    assert prompt_node == {
        "id": "0d1460e4-f207-4a69-bcea-7a3c7b325c02",
        "type": "PROMPT",
        "inputs": [
            {
                "id": "b99dec61-8c38-4b6b-96fa-cb83d5c9a9ef",
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
                "id": "6379398c-3c29-4327-9346-4d386a467f16",
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
            "output_id": "b9d579e2-b3ee-4524-917f-7329fc09af59",
            "error_output_id": None,
            "array_output_id": "547b4a00-eb16-4df5-92f4-cdd2fe7a0848",
            "source_handle_id": "7e29137d-af96-402c-8108-9a00e087d18e",
            "target_handle_id": "f8017ad7-14f2-4e6f-8456-a081db5ed7cd",
            "variant": "DEPLOYMENT",
            "prompt_deployment_id": deployment.id,
            "release_tag": "LATEST",
            "ml_model_fallbacks": None,
        },
        "display_data": {"position": {"x": 200.0, "y": -50.0}},
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
        "trigger": {
            "id": "f8017ad7-14f2-4e6f-8456-a081db5ed7cd",
            "merge_behavior": "AWAIT_ANY",
        },
        "ports": [{"id": "7e29137d-af96-402c-8108-9a00e087d18e", "name": "default", "type": "DEFAULT"}],
        "outputs": [
            {"id": "62bbe13a-9571-4165-9463-22092a04e450", "name": "json", "type": "JSON", "value": None},
            {"id": "b9d579e2-b3ee-4524-917f-7329fc09af59", "name": "text", "type": "STRING", "value": None},
            {"id": "547b4a00-eb16-4df5-92f4-cdd2fe7a0848", "name": "results", "type": "ARRAY", "value": None},
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
                                "node_id": "0d1460e4-f207-4a69-bcea-7a3c7b325c02",
                                "output_id": "62bbe13a-9571-4165-9463-22092a04e450",
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
        "display_data": {"position": {"x": 400.0, "y": -50.0}},
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
        "trigger": {
            "id": "58427684-3848-498a-8299-c6b0fc70265d",
            "merge_behavior": "AWAIT_ATTRIBUTES",
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
        "display_data": {"position": {"x": 600.0, "y": -50.0}},
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
            "id": "33e0220a-969a-4d38-86ac-0fe596ab2d88",
            "source_node_id": "32c7f398-277c-456b-9279-aa1f867fb637",
            "source_handle_id": "cc0f4028-1039-4063-971d-7dacbb01b379",
            "target_node_id": "0d1460e4-f207-4a69-bcea-7a3c7b325c02",
            "target_handle_id": "f8017ad7-14f2-4e6f-8456-a081db5ed7cd",
            "type": "DEFAULT",
        },
        {
            "id": "24f69a26-333c-4cf4-b12a-55979672923a",
            "source_node_id": "0d1460e4-f207-4a69-bcea-7a3c7b325c02",
            "source_handle_id": "7e29137d-af96-402c-8108-9a00e087d18e",
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
