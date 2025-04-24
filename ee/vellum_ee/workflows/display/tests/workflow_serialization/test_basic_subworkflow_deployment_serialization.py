from datetime import datetime
from uuid import uuid4

from deepdiff import DeepDiff

from vellum import WorkflowDeploymentRead
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_subworkflow_deployment.workflow import BasicSubworkflowDeploymentWorkflow


def test_serialize_workflow(vellum_client):
    # GIVEN a Workflow with stubbed out API calls
    deployment = WorkflowDeploymentRead(
        id=str(uuid4()),
        created=datetime.now(),
        label="Example Subworkflow Deployment",
        name="example_subworkflow_deployment",
        input_variables=[],
        output_variables=[],
        last_deployed_on=datetime.now(),
        last_deployed_history_item_id=str(uuid4()),
    )
    vellum_client.workflow_deployments.retrieve.return_value = deployment

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicSubworkflowDeploymentWorkflow)
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
                "id": "693cc9a5-8d74-4a58-bdcf-2b4989cdf250",
                "key": "city",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
            },
            {
                "id": "19a78824-9a98-4ae8-a1fc-61f81a422a17",
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
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {
                "id": "3f487916-126f-4d6c-95b4-fa72d875b793",
                "key": "temperature",
                "type": "NUMBER",
            },
            {
                "id": "45d53a1e-26e8-4c43-a010-80d141acc249",
                "key": "reasoning",
                "type": "STRING",
            },
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["edges"]) == 3
    assert len(workflow_raw_data["nodes"]) == 4

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "f0eea82b-39cc-44e3-9c0d-12205ed5652c",
        "type": "ENTRYPOINT",
        "base": None,
        "definition": None,
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "13d9eb34-aecb-496d-9e57-d5e786b0bc7c",
        },
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
        },
    }

    subworkflow_node = workflow_raw_data["nodes"][1]
    assert subworkflow_node == {
        "id": "d71f674e-8a6b-44ab-b552-7f4637a4e7a6",
        "type": "SUBWORKFLOW",
        "inputs": [
            {
                "id": "be426336-0844-4ebd-8cfe-efef60305b92",
                "key": "city",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "693cc9a5-8d74-4a58-bdcf-2b4989cdf250"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "8a7495b1-a7fc-405f-8ef6-ba05dd3f9e5c",
                "key": "date",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "19a78824-9a98-4ae8-a1fc-61f81a422a17"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Example Subworkflow Deployment Node",
            "error_output_id": None,
            "source_handle_id": "ab0db8a9-7b53-4d88-8667-273b31303273",
            "target_handle_id": "e4d80502-9281-42c8-91e3-10817bcd7d9e",
            "variant": "DEPLOYMENT",
            "workflow_deployment_id": deployment.id,
            "release_tag": "LATEST",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "module": ["vellum", "workflows", "nodes", "displayable", "subworkflow_deployment_node", "node"],
            "name": "SubworkflowDeploymentNode",
        },
        "definition": {
            "module": ["tests", "workflows", "basic_subworkflow_deployment", "workflow"],
            "name": "ExampleSubworkflowDeploymentNode",
        },
        "ports": [{"id": "ab0db8a9-7b53-4d88-8667-273b31303273", "name": "default", "type": "DEFAULT"}],
    }

    assert not DeepDiff(
        [
            {
                "id": "18170041-1a70-4836-9fa0-adceba2a1f4f",
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
                    "name": "temperature",
                    "target_handle_id": "23117248-df28-4519-bebc-abcb24f966b3",
                    "output_id": "3f487916-126f-4d6c-95b4-fa72d875b793",
                    "output_type": "NUMBER",
                    "node_input_id": "6f4955d8-8a3f-4db7-8293-7affc5877dcd",
                },
                "inputs": [
                    {
                        "id": "6f4955d8-8a3f-4db7-8293-7affc5877dcd",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "d71f674e-8a6b-44ab-b552-7f4637a4e7a6",
                                        "output_id": "5170e2fb-2b7c-4cb1-8958-6c0f2a359e1e",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 0.0, "y": 0.0}},
            },
            {
                "id": "94afd0ac-1ec4-486b-a6fb-fa1ec7029d19",
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
                    "name": "reasoning",
                    "target_handle_id": "c3aeba92-4faf-4814-9842-eec7436ee555",
                    "output_id": "45d53a1e-26e8-4c43-a010-80d141acc249",
                    "output_type": "STRING",
                    "node_input_id": "74337307-3fcb-42c5-9aed-98bd4a79caef",
                },
                "inputs": [
                    {
                        "id": "74337307-3fcb-42c5-9aed-98bd4a79caef",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "d71f674e-8a6b-44ab-b552-7f4637a4e7a6",
                                        "output_id": "d9ab77e4-226f-436f-ad70-585b57510001",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 0.0, "y": 0.0}},
            },
        ],
        workflow_raw_data["nodes"][2:],
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "77f5b6e0-16e3-4bb5-9344-4d9557289802",
                "source_handle_id": "13d9eb34-aecb-496d-9e57-d5e786b0bc7c",
                "source_node_id": "f0eea82b-39cc-44e3-9c0d-12205ed5652c",
                "target_handle_id": "e4d80502-9281-42c8-91e3-10817bcd7d9e",
                "target_node_id": "d71f674e-8a6b-44ab-b552-7f4637a4e7a6",
                "type": "DEFAULT",
            },
            {
                "id": "69933897-e91e-4c6c-9ba3-ed3e3c265c73",
                "source_handle_id": "ab0db8a9-7b53-4d88-8667-273b31303273",
                "source_node_id": "d71f674e-8a6b-44ab-b552-7f4637a4e7a6",
                "target_handle_id": "c3aeba92-4faf-4814-9842-eec7436ee555",
                "target_node_id": "94afd0ac-1ec4-486b-a6fb-fa1ec7029d19",
                "type": "DEFAULT",
            },
            {
                "id": "86a9af31-f78e-45ac-b170-f66bbba98f9d",
                "source_handle_id": "ab0db8a9-7b53-4d88-8667-273b31303273",
                "source_node_id": "d71f674e-8a6b-44ab-b552-7f4637a4e7a6",
                "target_handle_id": "23117248-df28-4519-bebc-abcb24f966b3",
                "target_node_id": "18170041-1a70-4836-9fa0-adceba2a1f4f",
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
        "name": "BasicSubworkflowDeploymentWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_subworkflow_deployment",
            "workflow",
        ],
    }
