import json
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import ChatMessage
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import create_function_node, create_tool_router_node
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
        parameters=DEFAULT_PROMPT_PARAMETERS,
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
        parameters=DEFAULT_PROMPT_PARAMETERS,
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
    outputs = list(function_node.run())

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


def test_tool_calling_node_with_user_provided_chat_history_block(vellum_adhoc_prompt_client):
    """
    Test that ToolCallingNode with user-provided chat history block merges user and node messages.
    """

    # GIVEN a ToolCallingNode with a user-provided chat history block
    user_chat_history_block = VariablePromptBlock(
        block_type="VARIABLE",
        input_variable="chat_history",
        state=None,
        cache_config=None,
    )

    class TestToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = [user_chat_history_block]
        functions = [first_function]
        prompt_inputs = {"chat_history": [ChatMessage(role="USER", text="Hello from user")]}
        max_prompt_iterations = 1

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[Any]:
        execution_id = str(uuid4())
        events = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=[StringVellumValue(value="Hello! I can help you.")],
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # AND a state
    state = BaseState()

    # WHEN the ToolCallingNode runs
    node = TestToolCallingNode(state=state)
    list(node.run())

    # THEN the API should be called with the correct blocks
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count >= 1

    # AND the blocks should include the user-provided chat_history block
    call_kwargs = mock_api.call_args.kwargs
    blocks = call_kwargs["blocks"]

    chat_history_blocks = [
        block for block in blocks if block.block_type == "VARIABLE" and block.input_variable == "chat_history"
    ]
    assert len(chat_history_blocks) == 1

    # AND the input_values should include the user's chat history
    input_values = call_kwargs["input_values"]
    chat_history_inputs = [
        input_val for input_val in input_values if hasattr(input_val, "key") and input_val.key == "chat_history"
    ]
    assert len(chat_history_inputs) == 1
    assert chat_history_inputs[0].value == [ChatMessage(role="USER", text="Hello from user")]
