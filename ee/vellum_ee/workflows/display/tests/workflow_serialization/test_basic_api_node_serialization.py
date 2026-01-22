import pytest
from datetime import datetime
from uuid import uuid4

from deepdiff import DeepDiff

from vellum import WorkspaceSecretRead
from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import APIRequestMethod, AuthorizationType
from vellum.workflows.nodes.displayable import APINode
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum_ee.workflows.display.utils.exceptions import UserFacingException
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_api_node.workflow import SimpleAPIWorkflow

# 0d76e1e1-3a4b-4eb4-a606-f73d62c -> a0542dcc-443c-4b3b-aac8-c41d2277a5c7


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
    workflow_display = get_workflow_display(workflow_class=SimpleAPIWorkflow)

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

    # AND the API node should be serialized correctly
    api_node = next(n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "APINode")

    assert api_node["id"] == "6783c80f-5fc0-4712-a251-ce59d3c14ff2"
    assert api_node["type"] == "API"

    assert api_node["base"]["name"] == "APINode"
    assert api_node["base"]["module"] == ["vellum", "workflows", "nodes", "displayable", "api_node", "node"]

    assert api_node["definition"]["name"] == "SimpleAPINode"
    assert api_node["definition"]["module"] == ["tests", "workflows", "basic_api_node", "workflow"]

    assert api_node["trigger"]["id"] == "35816b8f-453b-4f70-a5fc-72dd0ceca460"
    assert api_node["trigger"]["merge_behavior"] == "AWAIT_ANY"

    assert len(api_node["ports"]) == 1
    assert api_node["ports"][0]["name"] == "default"
    assert api_node["ports"][0]["type"] == "DEFAULT"

    assert len(api_node["outputs"]) == 4
    output_names = {output["name"] for output in api_node["outputs"]}
    assert output_names == {"json", "headers", "status_code", "text"}

    assert api_node["data"]["label"] == "Simple API Node"
    assert api_node["data"]["error_output_id"] is None
    assert api_node["data"]["source_handle_id"] == "6c574f01-9362-4edd-b3dd-5faacca76b28"
    assert api_node["data"]["target_handle_id"] == "35816b8f-453b-4f70-a5fc-72dd0ceca460"
    assert api_node["data"]["json_output_id"] == "a0542dcc-443c-4b3b-aac8-c41d2277a5c7"
    assert api_node["data"]["text_output_id"] == "f7190a6b-0c13-4a5a-9087-d8e6feb84eca"
    assert api_node["data"]["status_code_output_id"] == "f687c0a1-b63a-4c5c-b6ef-472c6108ae4b"

    input_keys = {inp["key"] for inp in api_node["inputs"]}
    assert "url" in input_keys
    assert "method" in input_keys
    assert "body" in input_keys

    assert len(api_node["attributes"]) == 1
    assert api_node["attributes"][0]["name"] == "timeout"

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


class ConstantApiKeyNode(APINode):
    method = APIRequestMethod.POST
    url = "https://api.example.com"
    authorization_type = AuthorizationType.API_KEY
    api_key_header_value = "hardcoded-secret-value"


class ConstantApiKeyWorkflow(BaseWorkflow):
    graph = ConstantApiKeyNode


class ConstantBearerTokenNode(APINode):
    method = APIRequestMethod.POST
    url = "https://api.example.com"
    authorization_type = AuthorizationType.BEARER_TOKEN
    bearer_token_value = "hardcoded-secret-value"


class ConstantBearerTokenWorkflow(BaseWorkflow):
    graph = ConstantBearerTokenNode


@pytest.mark.parametrize(
    "workflow_class",
    [ConstantApiKeyWorkflow, ConstantBearerTokenWorkflow],
    ids=["api_key_header_value", "bearer_token_value"],
)
def test_serialize_workflow__constant_secret_value__raises_error(workflow_class):
    """
    Tests that API nodes reject constant values for secret inputs.
    """

    # GIVEN a workflow with an API node that has a constant value for a secret input
    # WHEN we try to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=workflow_class)

    # THEN it should raise a UserFacingException
    with pytest.raises(UserFacingException) as exc_info:
        workflow_display.serialize()

    # AND the error message should explain the issue
    assert "Secret inputs cannot be set to constant values" in str(exc_info.value)
    assert "VellumSecretReference or EnvironmentVariableReference" in str(exc_info.value)


class SecretRefApiKeyNode(APINode):
    method = APIRequestMethod.POST
    url = "https://api.example.com"
    authorization_type = AuthorizationType.API_KEY
    api_key_header_value = VellumSecretReference("MY_SECRET")


class SecretRefApiKeyWorkflow(BaseWorkflow):
    graph = SecretRefApiKeyNode


class EnvVarRefApiKeyNode(APINode):
    method = APIRequestMethod.POST
    url = "https://api.example.com"
    authorization_type = AuthorizationType.API_KEY
    api_key_header_value = EnvironmentVariableReference(name="MY_ENV_VAR")


class EnvVarRefApiKeyWorkflow(BaseWorkflow):
    graph = EnvVarRefApiKeyNode


class SecretRefBearerTokenNode(APINode):
    method = APIRequestMethod.POST
    url = "https://api.example.com"
    authorization_type = AuthorizationType.BEARER_TOKEN
    bearer_token_value = VellumSecretReference("MY_SECRET")


class SecretRefBearerTokenWorkflow(BaseWorkflow):
    graph = SecretRefBearerTokenNode


class EnvVarRefBearerTokenNode(APINode):
    method = APIRequestMethod.POST
    url = "https://api.example.com"
    authorization_type = AuthorizationType.BEARER_TOKEN
    bearer_token_value = EnvironmentVariableReference(name="MY_ENV_VAR")


class EnvVarRefBearerTokenWorkflow(BaseWorkflow):
    graph = EnvVarRefBearerTokenNode


@pytest.mark.parametrize(
    "workflow_class",
    [
        SecretRefApiKeyWorkflow,
        EnvVarRefApiKeyWorkflow,
        SecretRefBearerTokenWorkflow,
        EnvVarRefBearerTokenWorkflow,
    ],
    ids=[
        "api_key_with_secret_ref",
        "api_key_with_env_var_ref",
        "bearer_token_with_secret_ref",
        "bearer_token_with_env_var_ref",
    ],
)
def test_serialize_workflow__secret_reference_values__succeeds(workflow_class, vellum_client):
    """
    Tests that API nodes accept VellumSecretReference and EnvironmentVariableReference for secret inputs.
    """

    # GIVEN a workflow with an API node that uses a secret or env var reference
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

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=workflow_class)
    serialized_workflow = workflow_display.serialize()

    # THEN it should serialize successfully
    assert "workflow_raw_data" in serialized_workflow
