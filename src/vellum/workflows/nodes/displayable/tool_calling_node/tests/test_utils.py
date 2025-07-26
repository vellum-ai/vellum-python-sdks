import pytest
from uuid import uuid4

from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import create_tool_router_node, get_function_name
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


def test_create_tool_router_node_max_prompt_iterations(vellum_adhoc_prompt_client):
    # GIVEN a tool router node with max_prompt_iterations set to None
    tool_router_node = create_tool_router_node(
        ml_model="gpt-4o-mini",
        blocks=[],
        functions=[],
        prompt_inputs=None,
        parameters=DEFAULT_PROMPT_PARAMETERS,
        max_prompt_iterations=None,
    )

    def generate_prompt_events(*args, **kwargs):
        execution_id = str(uuid4())
        events = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=[StringVellumValue(value="test output")],
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the tool router node
    node_instance = tool_router_node()
    outputs = list(node_instance.run())
    assert outputs[0].name == "results"
    assert outputs[0].value == [StringVellumValue(type="STRING", value="test output")]
    assert outputs[1].name == "text"
    assert outputs[1].value == "test output"
