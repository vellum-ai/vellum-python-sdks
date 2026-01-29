from datetime import datetime
from uuid import uuid4

from deepdiff import DeepDiff

from vellum import (
    ReleaseEnvironment,
    VellumVariable,
    WorkflowDeploymentRelease,
    WorkflowDeploymentReleaseWorkflowDeployment,
    WorkflowDeploymentReleaseWorkflowVersion,
)
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import SubworkflowDeploymentNode, TemplatingNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_subworkflow_deployment.workflow import BasicSubworkflowDeploymentWorkflow


def test_serialize_workflow(vellum_client):
    # GIVEN a Workflow with stubbed out API calls
    deployment_id = str(uuid4())
    deployment_release = WorkflowDeploymentRelease(
        id=str(uuid4()),
        created=datetime.now(),
        environment=ReleaseEnvironment(id=str(uuid4()), name="DEVELOPMENT", label="Development"),
        workflow_version=WorkflowDeploymentReleaseWorkflowVersion(
            id=str(uuid4()),
            input_variables=[],
            output_variables=[],
        ),
        deployment=WorkflowDeploymentReleaseWorkflowDeployment(
            id=deployment_id,
            name="example_subworkflow_deployment",
        ),
        release_tags=[],
        reviews=[],
    )
    vellum_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = deployment_release

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
                "schema": {"type": "string"},
            },
            {
                "id": "19a78824-9a98-4ae8-a1fc-61f81a422a17",
                "key": "date",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
                "schema": {"type": "string"},
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
            "position": {"x": 0.0, "y": 0.0},
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
            "workflow_deployment_id": deployment_id,
            "release_tag": "LATEST",
        },
        "attributes": [
            {
                "id": "1453965b-dc73-4afc-956b-6cf9cc83b951",
                "name": "subworkflow_inputs",
                "value": {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "a6927bc5-ceff-48dc-93ba-488b0b339658",
                            "key": "city",
                            "value": {
                                "type": "WORKFLOW_INPUT",
                                "input_variable_id": "693cc9a5-8d74-4a58-bdcf-2b4989cdf250",
                            },
                        },
                        {
                            "id": "298283f8-75d2-4632-b74e-79b777170d3d",
                            "key": "date",
                            "value": {
                                "type": "WORKFLOW_INPUT",
                                "input_variable_id": "19a78824-9a98-4ae8-a1fc-61f81a422a17",
                            },
                        },
                    ],
                },
            }
        ],
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
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
        "outputs": [
            {
                "id": "d901cbed-9905-488c-be62-e2668f85438f",
                "name": "temperature",
                "schema": {"type": "number"},
                "type": "NUMBER",
                "value": None,
            },
            {
                "id": "68de689c-fe8a-4189-b7d0-82c620ac30f9",
                "name": "reasoning",
                "schema": {"type": "string"},
                "type": "STRING",
                "value": None,
            },
        ],
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


def test_serialize_workflow__subworkflow_deployment_node_outputs_from_release(vellum_client):
    """
    Tests that subworkflow deployment node outputs are populated from the deployment's output variables,
    and that downstream nodes referencing those outputs correctly reference the subworkflow node.
    """

    # GIVEN a subworkflow deployment node with foo and bar outputs
    class SubworkflowDeploymentNodeWithOutputs(SubworkflowDeploymentNode):
        deployment = "test_subworkflow_deployment"

        class Outputs(BaseOutputs):
            foo: str
            bar: int

    # AND a templating node that references both outputs
    class ConsumingNode(TemplatingNode):
        template = "foo: {{ foo }}, bar: {{ bar }}"
        inputs = {
            "foo": SubworkflowDeploymentNodeWithOutputs.Outputs.foo,
            "bar": SubworkflowDeploymentNodeWithOutputs.Outputs.bar,
        }

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SubworkflowDeploymentNodeWithOutputs >> ConsumingNode

        class Outputs(BaseOutputs):
            result = ConsumingNode.Outputs.result

    # AND a deployment release with output variables for foo and bar
    foo_output_id = "11111111-1111-1111-1111-111111111111"
    bar_output_id = "22222222-2222-2222-2222-222222222222"
    deployment_release = WorkflowDeploymentRelease(
        id=str(uuid4()),
        created=datetime.now(),
        environment=ReleaseEnvironment(id=str(uuid4()), name="DEVELOPMENT", label="Development"),
        workflow_version=WorkflowDeploymentReleaseWorkflowVersion(
            id=str(uuid4()),
            input_variables=[],
            output_variables=[
                VellumVariable(id=foo_output_id, key="foo", type="STRING"),
                VellumVariable(id=bar_output_id, key="bar", type="NUMBER"),
            ],
        ),
        deployment=WorkflowDeploymentReleaseWorkflowDeployment(
            id=str(uuid4()),
            name="test_subworkflow_deployment",
        ),
        release_tags=[],
        reviews=[],
    )
    vellum_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = deployment_release

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the subworkflow deployment node should have outputs populated from the deployment's output variables
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    subworkflow_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "SUBWORKFLOW")

    # AND the outputs should contain foo and bar with the correct IDs from the deployment
    assert subworkflow_node.get("outputs") is not None, "outputs field should not be None"
    outputs = subworkflow_node["outputs"]
    assert len(outputs) == 2

    foo_output = next((o for o in outputs if o["name"] == "foo"), None)
    bar_output = next((o for o in outputs if o["name"] == "bar"), None)

    assert foo_output is not None, "foo output should exist"
    assert bar_output is not None, "bar output should exist"
    assert foo_output["id"] == foo_output_id, "foo output ID should match deployment's output variable ID"
    assert bar_output["id"] == bar_output_id, "bar output ID should match deployment's output variable ID"
    assert foo_output["type"] == "STRING"
    assert bar_output["type"] == "NUMBER"

    # AND the consuming node should reference the subworkflow node's outputs
    consuming_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "TEMPLATING")
    consuming_node_inputs = consuming_node["inputs"]

    foo_input = next((inp for inp in consuming_node_inputs if inp["key"] == "foo"), None)
    bar_input = next((inp for inp in consuming_node_inputs if inp["key"] == "bar"), None)

    assert foo_input is not None, "foo input should exist on consuming node"
    assert bar_input is not None, "bar input should exist on consuming node"

    # AND the foo input should reference the subworkflow node
    foo_rule = foo_input["value"]["rules"][0]
    assert foo_rule["type"] == "NODE_OUTPUT"
    assert foo_rule["data"]["node_id"] == subworkflow_node["id"]
    # The output_id should match the foo output from the subworkflow node's outputs list
    assert foo_rule["data"]["output_id"] == foo_output["id"]

    # AND the bar input should reference the subworkflow node
    bar_rule = bar_input["value"]["rules"][0]
    assert bar_rule["type"] == "NODE_OUTPUT"
    assert bar_rule["data"]["node_id"] == subworkflow_node["id"]
    # The output_id should match the bar output from the subworkflow node's outputs list
    assert bar_rule["data"]["output_id"] == bar_output["id"]


def test_serialize_workflow__wrapped_subworkflow_deployment_node_calls_build_once(vellum_client):
    """
    Tests that a SubworkflowDeploymentNode wrapped in TryNode only calls the deployment
    release API once during serialization, and that the serialized output contains the
    correct deployment_id and release_tag.
    """

    # GIVEN a SubworkflowDeploymentNode wrapped in TryNode
    @TryNode.wrap()
    class WrappedSubworkflowDeploymentNode(SubworkflowDeploymentNode):
        deployment = "test_wrapped_subworkflow_deployment"
        release_tag = "LATEST"

        class Outputs(BaseOutputs):
            result: str

    # AND a workflow that uses the wrapped node
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = WrappedSubworkflowDeploymentNode

        class Outputs(BaseOutputs):
            final_result = WrappedSubworkflowDeploymentNode.Outputs.result

    # AND a deployment release with specific deployment_id and release_tag
    deployment_id = "test-deployment-id-12345"
    result_output_id = "result-output-id-67890"
    deployment_release = WorkflowDeploymentRelease(
        id=str(uuid4()),
        created=datetime.now(),
        environment=ReleaseEnvironment(id=str(uuid4()), name="DEVELOPMENT", label="Development"),
        workflow_version=WorkflowDeploymentReleaseWorkflowVersion(
            id=str(uuid4()),
            input_variables=[],
            output_variables=[
                VellumVariable(id=result_output_id, key="result", type="STRING"),
            ],
        ),
        deployment=WorkflowDeploymentReleaseWorkflowDeployment(
            id=deployment_id,
            name="test_wrapped_subworkflow_deployment",
        ),
        release_tags=[],
        reviews=[],
    )
    vellum_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = deployment_release

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the deployment release API should only be called once
    assert vellum_client.workflow_deployments.retrieve_workflow_deployment_release.call_count == 1

    # AND the serialized subworkflow node should have the correct deployment_id
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    subworkflow_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "SUBWORKFLOW")
    assert subworkflow_node["data"]["workflow_deployment_id"] == deployment_id

    # AND the serialized subworkflow node should have the correct release_tag
    assert subworkflow_node["data"]["release_tag"] == "LATEST"
