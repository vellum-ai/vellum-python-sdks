from datetime import datetime
from uuid import uuid4

from deepdiff import DeepDiff

from vellum import WorkspaceSecretRead
from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_api_node.workflow import SimpleAPIWorkflow


def test_serialize_workflow(vellum_client):
    # GIVEN a Workflow that uses a vellum API node
    # AND stubbed out API calls
    workspace_secret_id = str(uuid4())
    workspace_secret = WorkspaceSecretRead(
        id=workspace_secret_id,
        modified=datetime.now(),
        name="MY_SECRET",
        label="My Secret",
        secret_type="USER_DEFINED",
    )
    vellum_client.workspace_secrets.retrieve.return_value = workspace_secret

    # WHEN we serialize it
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=SimpleAPIWorkflow)

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
    assert len(input_variables) == 0

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 3
    assert not DeepDiff(
        [
            {"id": "9a37bf7d-484e-4725-903e-f3254df38a0a", "key": "json", "type": "JSON"},
            {"id": "5090e96d-5787-4a08-bf58-129101cf2548", "key": "headers", "type": "JSON"},
            {"id": "44ea8d75-e2a8-4627-85b1-8504b65d25c9", "key": "status_code", "type": "NUMBER"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert workflow_raw_data.keys() == {"edges", "nodes", "display_data", "definition"}
    assert len(workflow_raw_data["edges"]) == 4
    assert len(workflow_raw_data["nodes"]) == 5

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "3a6b1467-5c83-4bcd-86a0-6415bc32d23b",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "8eaa7f02-25ff-4a00-9b0a-5185718d89b3"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
    }

    api_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "facb80d7-ee08-42a0-82a9-ee26a9218185",
            "type": "API",
            "inputs": [
                {
                    "id": "cd8a19f4-4eb7-4359-a8a6-918569c466a5",
                    "key": "url",
                    "value": {
                        "rules": [
                            {"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "https://api.vellum.ai"}}
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "fd61b5ac-39f9-4cfe-a839-f8ce78c202df",
                    "key": "method",
                    "value": {
                        "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "POST"}}],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "c3a17ceb-e201-4025-b18a-9162aac7705e",
                    "key": "body",
                    "value": {
                        "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "JSON", "value": {"key": "value"}}}],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "3092bf23-3202-4f3e-874c-9a33ccc73459",
                    "key": "authorization_type",
                    "value": {
                        "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "API_KEY"}}],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "fee5e3c9-442a-4922-ba80-5ee07361cea7",
                    "key": "bearer_token_value",
                    "value": {
                        "rules": [
                            {"type": "WORKSPACE_SECRET", "data": {"type": "STRING", "workspace_secret_id": None}}
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "2fcdfbc3-8095-4277-bb4a-a201fd326b54",
                    "key": "api_key_header_key",
                    "value": {
                        "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "CUSTOM_API_KEY"}}],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "d794bb51-a419-4fd8-be63-dfaf4166e831",
                    "key": "api_key_header_value",
                    "value": {
                        "rules": [
                            {
                                "type": "WORKSPACE_SECRET",
                                "data": {
                                    "type": "STRING",
                                    "workspace_secret_id": f"{workspace_secret_id}",
                                },
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "57c31247-998a-430d-bb62-bf50eca7df35",
                    "key": "additional_header_key",
                    "value": {
                        "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "additional_header"}}],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "47b32274-f19b-4c15-b788-55c069c311c5",
                    "key": "additional_header_value",
                    "value": {
                        "rules": [
                            {"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "additional header value"}}
                        ],
                        "combinator": "OR",
                    },
                },
            ],
            "data": {
                "label": "Simple A P I Node",
                "error_output_id": None,
                "source_handle_id": "7c33b4d3-9204-4bd5-9371-80ee34f83073",
                "target_handle_id": "14b538a5-aedb-41f3-b579-039956b7c7ed",
                "url_input_id": "cd8a19f4-4eb7-4359-a8a6-918569c466a5",
                "method_input_id": "fd61b5ac-39f9-4cfe-a839-f8ce78c202df",
                "body_input_id": "c3a17ceb-e201-4025-b18a-9162aac7705e",
                "authorization_type_input_id": "3092bf23-3202-4f3e-874c-9a33ccc73459",
                "bearer_token_value_input_id": "fee5e3c9-442a-4922-ba80-5ee07361cea7",
                "api_key_header_key_input_id": "2fcdfbc3-8095-4277-bb4a-a201fd326b54",
                "api_key_header_value_input_id": "d794bb51-a419-4fd8-be63-dfaf4166e831",
                "additional_headers": [
                    {
                        "header_key_input_id": "57c31247-998a-430d-bb62-bf50eca7df35",
                        "header_value_input_id": "47b32274-f19b-4c15-b788-55c069c311c5",
                    }
                ],
                "text_output_id": "17342c21-12bb-49ab-88ce-f144e0376b32",
                "json_output_id": "12e4a99d-883d-4da5-aa51-35817d94013e",
                "status_code_output_id": "fecc16c3-400e-4fd3-8223-08366070e3b1",
            },
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "name": "APINode",
                "module": ["vellum", "workflows", "nodes", "displayable", "api_node", "node"],
            },
            "definition": {
                "name": "SimpleAPINode",
                "module": ["tests", "workflows", "basic_api_node", "workflow"],
            },
        },
        api_node,
    )

    final_output_nodes = workflow_raw_data["nodes"][2:5]
    assert not DeepDiff(
        [
            {
                "id": "8f975ab1-aca6-4dc1-aa80-c596f4e13afa",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "json",
                    "target_handle_id": "06853542-e1a1-4a00-bd1e-4ac40f347b32",
                    "output_id": "9a37bf7d-484e-4725-903e-f3254df38a0a",
                    "output_type": "JSON",
                    "node_input_id": "b49f0f85-37fc-4686-81a7-287c06634661",
                },
                "inputs": [
                    {
                        "id": "b49f0f85-37fc-4686-81a7-287c06634661",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "facb80d7-ee08-42a0-82a9-ee26a9218185",
                                        "output_id": "12e4a99d-883d-4da5-aa51-35817d94013e",
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
            },
            {
                "id": "736f9bd0-f487-42af-bdb3-780b4941c61c",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "headers",
                    "target_handle_id": "80d0894f-642e-4d2e-b43a-f236e7bedb3c",
                    "output_id": "5090e96d-5787-4a08-bf58-129101cf2548",
                    "output_type": "JSON",
                    "node_input_id": "5e892e5b-0004-4a04-bd2e-1ea9e0e5d3f9",
                },
                "inputs": [
                    {
                        "id": "5e892e5b-0004-4a04-bd2e-1ea9e0e5d3f9",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "facb80d7-ee08-42a0-82a9-ee26a9218185",
                                        "output_id": "0d76e1e1-3a4b-4eb4-a606-f73d62cf1a7e",
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
            },
            {
                "id": "3f3ffc50-b156-48ac-b5f3-f68cb05c2b90",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "status_code",
                    "target_handle_id": "0c98c306-b519-40d7-8b05-321b1dfd7f11",
                    "output_id": "44ea8d75-e2a8-4627-85b1-8504b65d25c9",
                    "output_type": "NUMBER",
                    "node_input_id": "14345321-7e6b-4e2a-918a-7a5b0064f047",
                },
                "inputs": [
                    {
                        "id": "14345321-7e6b-4e2a-918a-7a5b0064f047",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "facb80d7-ee08-42a0-82a9-ee26a9218185",
                                        "output_id": "fecc16c3-400e-4fd3-8223-08366070e3b1",
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
            },
        ],
        final_output_nodes,
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "3c7551f5-0a76-4274-953e-c048b15f560a",
                "source_node_id": "3a6b1467-5c83-4bcd-86a0-6415bc32d23b",
                "source_handle_id": "8eaa7f02-25ff-4a00-9b0a-5185718d89b3",
                "target_node_id": "facb80d7-ee08-42a0-82a9-ee26a9218185",
                "target_handle_id": "14b538a5-aedb-41f3-b579-039956b7c7ed",
                "type": "DEFAULT",
            },
            {
                "id": "422bbbb7-38b2-4e19-ac95-24a86ed24100",
                "source_node_id": "facb80d7-ee08-42a0-82a9-ee26a9218185",
                "source_handle_id": "7c33b4d3-9204-4bd5-9371-80ee34f83073",
                "target_node_id": "8f975ab1-aca6-4dc1-aa80-c596f4e13afa",
                "target_handle_id": "06853542-e1a1-4a00-bd1e-4ac40f347b32",
                "type": "DEFAULT",
            },
            {
                "id": "73007fe0-5cc2-435e-b2e4-6fa734153fbd",
                "source_node_id": "facb80d7-ee08-42a0-82a9-ee26a9218185",
                "source_handle_id": "7c33b4d3-9204-4bd5-9371-80ee34f83073",
                "target_node_id": "736f9bd0-f487-42af-bdb3-780b4941c61c",
                "target_handle_id": "80d0894f-642e-4d2e-b43a-f236e7bedb3c",
                "type": "DEFAULT",
            },
            {
                "id": "4ac7d1c4-697b-440c-a35d-61ffb44a33b3",
                "source_node_id": "facb80d7-ee08-42a0-82a9-ee26a9218185",
                "source_handle_id": "7c33b4d3-9204-4bd5-9371-80ee34f83073",
                "target_node_id": "3f3ffc50-b156-48ac-b5f3-f68cb05c2b90",
                "target_handle_id": "0c98c306-b519-40d7-8b05-321b1dfd7f11",
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
        "name": "SimpleAPIWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_api_node",
            "workflow",
        ],
    }
