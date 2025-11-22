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
            "position": {"x": 0.0, "y": -50.0},
        },
    }

    subworkflow_node = workflow_raw_data["nodes"][1]
    assert subworkflow_node == {
        "id": "bb98a2c4-c9a7-4c39-8f31-dc7961dc9996",
        "type": "SUBWORKFLOW",
        "inputs": [
            {
                "id": "8107cec2-8215-4730-b52c-859e87a1c116",
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
                "id": "3487e51a-e7fe-4b2c-a1f9-f72c83a329db",
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
            "source_handle_id": "ff99bf0c-c239-4b8b-8ac1-483b134f94f4",
            "target_handle_id": "d6194ccf-d31b-4846-8e24-3e189d84351a",
            "variant": "DEPLOYMENT",
            "workflow_deployment_id": deployment.id,
            "release_tag": "LATEST",
        },
        "display_data": {"position": {"x": 200.0, "y": -50.0}, "icon": "vellum:icon:diagram-sankey", "color": "grass"},
        "base": {
            "module": ["vellum", "workflows", "nodes", "displayable", "subworkflow_deployment_node", "node"],
            "name": "SubworkflowDeploymentNode",
        },
        "definition": {
            "module": ["tests", "workflows", "basic_subworkflow_deployment", "workflow"],
            "name": "ExampleSubworkflowDeploymentNode",
        },
        "trigger": {
            "id": "d6194ccf-d31b-4846-8e24-3e189d84351a",
            "merge_behavior": "AWAIT_ANY",
        },
        "ports": [{"id": "ff99bf0c-c239-4b8b-8ac1-483b134f94f4", "name": "default", "type": "DEFAULT"}],
    }

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
