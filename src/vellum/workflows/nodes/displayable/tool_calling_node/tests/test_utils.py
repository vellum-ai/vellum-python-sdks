import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import get_function_name
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import ComposioToolDefinition, DeploymentDefinition


def test_get_function_name_callable():
    """Test callable"""

    def my_function() -> str:
        return "test"

    function = my_function

    result = get_function_name(function)

    assert result == "my_function"


def test_get_function_name_workflow_class():
    """Test workflow class."""

    class MyWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        class MyNode(BaseNode):
            class Outputs(BaseOutputs):
                result: str

            def run(self) -> Outputs:
                return self.Outputs(result="test")

        graph = MyNode

    workflow_class = MyWorkflow

    result = get_function_name(workflow_class)

    assert result == "my_workflow"


def test_get_function_name_subworkflow_deployment():
    """Test subworkflow deployment."""
    deployment_config = DeploymentDefinition(deployment="my-test-deployment", release_tag="v1.0.0")

    result = get_function_name(deployment_config)

    assert result == "mytestdeployment"


def test_get_function_name_subworkflow_deployment_uuid():
    """Test subworkflow deployment with UUID."""
    deployment_config = DeploymentDefinition(deployment="57f09beb-b463-40e0-bf9e-c972e664352f", release_tag="v1.0.0")

    result = get_function_name(deployment_config)

    assert result == "57f09bebb46340e0bf9ec972e664352f"


@pytest.mark.parametrize(
    "toolkit,action,description,expected_result",
    [
        ("SLACK", "SLACK_SEND_MESSAGE", "Send message to Slack", "slack_send_message"),
        ("GMAIL", "GMAIL_CREATE_EMAIL_DRAFT", "Create Gmail draft", "gmail_create_email_draft"),
    ],
)
def test_get_function_name_composio_tool_definition_various_toolkits(
    toolkit: str, action: str, description: str, expected_result: str
):
    """Test ComposioToolDefinition function name generation with various toolkits."""
    composio_tool = ComposioToolDefinition(toolkit=toolkit, action=action, description=description)

    result = get_function_name(composio_tool)

    assert result == expected_result
