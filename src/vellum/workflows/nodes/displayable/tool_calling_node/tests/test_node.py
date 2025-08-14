import json
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import ChatMessage
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.nodes.displayable.tool_calling_node.utils import (
    create_function_node,
    create_router_node,
    create_tool_prompt_node,
)
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.definition import DeploymentDefinition
from vellum.workflows.workflows.event_filters import all_workflow_event_filter


def first_function() -> str:
    return "first_function"


def second_function() -> str:
    return "second_function"


def test_port_condition_match_function_name():
    """
    Test that the port condition correctly matches the function name.
    """
    # GIVEN a tool prompt node
    tool_prompt_node = create_tool_prompt_node(
        ml_model="test-model",
        blocks=[],
        functions=[first_function, second_function],
        prompt_inputs=None,
        parameters=DEFAULT_PROMPT_PARAMETERS,
    )

    # AND a router node that references the tool prompt node
    router_node = create_router_node(
        functions=[first_function, second_function],
        tool_prompt_node=tool_prompt_node,
    )

    # AND a state with a function call to the first function
    state = ToolCallingState(
        meta=StateMeta(
            node_outputs={
                tool_prompt_node.Outputs.results: [
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

    # GIVEN a tool prompt node
    tool_prompt_node = create_tool_prompt_node(
        ml_model="test-model",
        blocks=[],
        functions=[MyWorkflow],
        prompt_inputs=None,
        parameters=DEFAULT_PROMPT_PARAMETERS,
    )

    # WHEN we create a function node for the workflow
    function_node_class = create_function_node(
        function=MyWorkflow,
        tool_prompt_node=tool_prompt_node,
    )

    # AND we create an instance with a context containing generated_files
    function_node = function_node_class()

    # Create a parent context with test data
    parent_context = WorkflowContext(
        generated_files={"script.py": "print('hello world')"},
    )
    function_node._context = parent_context

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


def test_tool_calling_node_with_generic_type_parameter():
    # GIVEN a custom state class
    class State(BaseState):
        pass

    # AND a ToolCallingNode that uses the generic type parameter
    class TestToolCallingNode(ToolCallingNode[State]):
        ml_model = "gpt-4o-mini"
        blocks = []
        functions = [first_function]
        max_prompt_iterations = 1

    # WHEN we create an instance of the node
    state = State()
    node = TestToolCallingNode(state=state)

    # THEN the node should be created successfully
    assert node is not None
    assert isinstance(node, TestToolCallingNode)
    assert node.state == state


def test_tool_calling_node_workflow_is_dynamic(vellum_adhoc_prompt_client):
    """
    Test workflow_version_exec_config without any mocks to see if that's the issue.
    """

    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"var_1": 1, "var_2": 2},
                        id="call_123",
                        name="add_numbers_workflow",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [StringVellumValue(value="The result is 3")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    class AddNode(BaseNode):

        class Outputs(BaseNode.Outputs):
            result: int

        def run(self) -> Outputs:
            return self.Outputs(result=1)

    class AddNumbersWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        """
        A simple workflow that adds two numbers.
        """

        graph = AddNode

        class Outputs(BaseWorkflow.Outputs):
            result = AddNode.Outputs.result

    class TestToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = []
        functions = [AddNumbersWorkflow]
        prompt_inputs = {}

    # GIVEN a workflow with just a tool calling node
    class ToolCallingWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = TestToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            text: str = TestToolCallingNode.Outputs.text
            chat_history: List[ChatMessage] = TestToolCallingNode.Outputs.chat_history

    workflow = ToolCallingWorkflow()

    # WHEN the workflow is executed and we capture all events
    events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # AND we should find workflow execution initiated events
    initiated_events = [event for event in events if event.name == "workflow.execution.initiated"]
    assert len(initiated_events) == 3  # Main workflow + tool calling internal + inline workflow

    assert initiated_events[0].body.workflow_definition.is_dynamic is False  # Main workflow
    assert initiated_events[1].body.workflow_definition.is_dynamic is True  # Tool calling internal
    assert initiated_events[2].body.workflow_definition.is_dynamic is True  # Inline workflow
