from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import create_function_node, get_function_name
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


def test_get_function_name_composio_tool_definition():
    """Test ComposioToolDefinition function name generation."""
    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )

    result = get_function_name(composio_tool)

    assert result == "github_github_create_an_issue"


def test_get_function_name_composio_tool_definition_various_toolkits():
    """Test ComposioToolDefinition function name generation with various toolkits."""
    slack_tool = ComposioToolDefinition(
        toolkit="SLACK", action="SLACK_SEND_MESSAGE", description="Send message to Slack"
    )

    gmail_tool = ComposioToolDefinition(
        toolkit="GMAIL", action="GMAIL_CREATE_EMAIL_DRAFT", description="Create Gmail draft"
    )

    assert get_function_name(slack_tool) == "slack_slack_send_message"
    assert get_function_name(gmail_tool) == "gmail_gmail_create_email_draft"


def test_create_function_node_with_composio_tool_definition():
    """Test that create_function_node creates ComposioFunctionNode for ComposioToolDefinition."""
    from unittest.mock import Mock

    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )

    # Mock tool router node
    mock_tool_router_node = Mock()
    mock_tool_router_node.Outputs.results = "mock_results"

    # Create function node
    function_node_class = create_function_node(composio_tool, mock_tool_router_node)

    # Check that it returns a class
    assert isinstance(function_node_class, type)

    # Check that the class name is correct
    assert function_node_class.__name__ == "ComposioFunctionNode_github_github_create_an_issue"

    # Check that it has the correct attributes
    assert hasattr(function_node_class, "composio_tool")
    assert hasattr(function_node_class, "function_call_output")

    # Check that the attributes exist (they are wrapped in NodeReference objects)
    assert hasattr(function_node_class.composio_tool, "__class__")
    assert hasattr(function_node_class.function_call_output, "__class__")


def test_create_function_node_composio_tool_inheritance():
    """Test that ComposioFunctionNode created by create_function_node has correct inheritance."""
    from unittest.mock import Mock

    from vellum.workflows.nodes.displayable.tool_calling_node.utils import ComposioFunctionNode

    composio_tool = ComposioToolDefinition(
        toolkit="SLACK", action="SLACK_SEND_MESSAGE", description="Send message to Slack"
    )

    # Mock tool router node
    mock_tool_router_node = Mock()
    mock_tool_router_node.Outputs.results = "mock_results"

    # Create function node
    function_node_class = create_function_node(composio_tool, mock_tool_router_node)

    # Check that it's a subclass of ComposioFunctionNode
    assert issubclass(function_node_class, ComposioFunctionNode)

    # Check that it's a subclass of BaseNode (through ComposioFunctionNode)
    assert issubclass(function_node_class, BaseNode)
