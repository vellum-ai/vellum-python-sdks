import json
from typing import Any, List

from vellum import ChatMessage
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.experimental.tool_calling_node.utils import create_function_node, create_tool_router_node
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.definition import DeploymentDefinition


def first_function() -> str:
    return "first_function"


def second_function() -> str:
    return "second_function"


def test_port_condition_match_function_name():
    """
    Test that the port condition correctly matches the function name.
    """
    # GIVEN a tool router node
    router_node = create_tool_router_node(
        ml_model="test-model",
        blocks=[],
        functions=[first_function, second_function],
        prompt_inputs=None,
    )

    # AND a state with a function call to the first function
    state = BaseState(
        meta=StateMeta(
            node_outputs={
                router_node.Outputs.results: [
                    FunctionCallVellumValue(
                        value=FunctionCall(
                            arguments={}, id="call_zp7pBQjGAOBCr7lo0AbR1HXT", name="first_function", state="FULFILLED"
                        ),
                    )
                ],
            },
        )
    )

    # WHEN the port condition is resolved
    # THEN the first function port should be true
    first_function_port = getattr(router_node.Ports, "first_function")
    assert first_function_port.resolve_condition(state) is True

    # AND the second function port should be false
    second_function_port = getattr(router_node.Ports, "second_function")
    assert second_function_port.resolve_condition(state) is False

    # AND the default port should be false
    default_port = getattr(router_node.Ports, "default")
    assert default_port.resolve_condition(state) is False


def test_tool_calling_node_inline_workflow_context():
    """
    Test that the tool calling node correctly passes the context to the inline workflow.
    This specifically tests that inline workflows receive the correct context.
    """

    # GIVEN a test workflow that captures its context
    class MyNode(BaseNode):
        class Outputs(BaseOutputs):
            generated_files: Any

        def run(self) -> Outputs:
            return self.Outputs(generated_files=self._context.generated_files)

    class MyWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyNode

        class Outputs(BaseOutputs):
            generated_files = MyNode.Outputs.generated_files

    # GIVEN a tool router node
    tool_router_node = create_tool_router_node(
        ml_model="test-model",
        blocks=[],
        functions=[MyWorkflow],
        prompt_inputs=None,
    )

    # WHEN we create a function node for the workflow
    function_node_class = create_function_node(
        function=MyWorkflow,
        tool_router_node=tool_router_node,
    )

    # AND we create an instance with a context containing generated_files
    function_node = function_node_class()

    # Create a parent context with test data
    parent_context = WorkflowContext(
        generated_files={"script.py": "print('hello world')"},
    )
    function_node._context = parent_context

    # Create a state with chat_history for the function node
    class TestState(BaseState):
        chat_history: List[ChatMessage] = []

    function_node.state = TestState(meta=StateMeta(node_outputs={tool_router_node.Outputs.text: '{"arguments": {}}'}))

    # WHEN the function node runs
    outputs = function_node.run()

    # THEN the workflow should have run successfully
    assert outputs is not None

    # AND the chat history should contain a function response
    assert len(function_node.state.chat_history) == 1
    function_response = function_node.state.chat_history[0]
    assert function_response.role == "FUNCTION"

    # AND the response should contain the generated files
    assert isinstance(function_response.content, StringChatMessageContent)
    data = json.loads(function_response.content.value)
    assert data["generated_files"] == {"script.py": "print('hello world')"}


def test_deployment_definition_release_tag_defaults_to_latest():
    """
    Test that when creating a DeploymentDefinition without specifying release_tag,
    it defaults to "LATEST".
    """
    # WHEN we create a deployment definition without specifying release_tag
    deployment_config = DeploymentDefinition(deployment="test-deployment")

    # THEN the release_tag should default to "LATEST"
    assert deployment_config.release_tag == "LATEST"
