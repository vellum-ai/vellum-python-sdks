import time
from unittest import mock
from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.ad_hoc_expand_meta import AdHocExpandMeta
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_request_json_input import PromptRequestJsonInput
from vellum.client.types.prompt_request_string_input import PromptRequestStringInput
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.client.types.vellum_variable import VellumVariable
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.tool_calling_node_parallel_execution.workflow import (
    ToolCallingNodeParallelExecutionEnabledWorkflow,
    ToolCallingNodeParallelExecutionWorkflow,
)


def test_parallel_tool_calls_parallel(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Test that verifies parallel tool execution with mixed function types.

    Two function nodes and one subworkflow node, each taking 0.5s,
    should execute in parallel, taking approximately 0.5s total.
    """

    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: list[PromptOutput]

        if call_count == 1:
            # First LLM call returns all three function calls
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={},
                        id="call_slow_tool_one",
                        name="slow_tool_one",
                        state="FULFILLED",
                    ),
                ),
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={},
                        id="call_slow_tool_two",
                        name="slow_tool_two",
                        state="FULFILLED",
                    ),
                ),
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={},
                        id="call_slow_tool_three_workflow",
                        name="slow_tool_three_workflow",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            # Second LLM call returns final response
            expected_outputs = [StringVellumValue(value="All three slow tools executed successfully.")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    # Set up the mock to return our events
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    first_call_input_id = uuid4_generator()
    first_call_input_id_2 = uuid4_generator()
    uuid4_generator()
    uuid4_generator()

    # GIVEN a parallel tool execution workflow
    workflow = ToolCallingNodeParallelExecutionWorkflow()

    # WHEN the workflow is executed and we measure time
    start_time = time.time()
    terminal_event = workflow.run()
    end_time = time.time()
    total_time = end_time - start_time

    # THEN the workflow is executed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs.text == "All three slow tools executed successfully."

    # AND the execution took approximately 0.5 seconds (parallel: max(0.5, 0.5, 0.5))
    assert total_time >= 1.5

    # AND the chat history shows all three tools were executed (order may vary in parallel mode)
    chat_history = terminal_event.outputs.chat_history
    assert len(chat_history) == 5  # 1 function calls message + 3 function results + 1 final response

    assert chat_history[0].role == "ASSISTANT"  # First function call (all three)
    assert chat_history[1].role == "FUNCTION"  # First result
    assert chat_history[2].role == "FUNCTION"  # Second result
    assert chat_history[3].role == "FUNCTION"  # Third result
    assert chat_history[4].role == "ASSISTANT"  # Final response

    function_results = [msg for msg in chat_history if msg.role == "FUNCTION"]
    assert len(function_results) == 3

    first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
    assert first_call.kwargs == {
        "ml_model": "gpt-4o-mini",
        "input_values": [
            PromptRequestStringInput(
                key="question", type="STRING", value="Execute all three slow tools and summarize the results."
            ),
            PromptRequestJsonInput(key="chat_history", type="JSON", value=[]),
        ],
        "input_variables": [
            VellumVariable(
                id=str(first_call_input_id),
                key="question",
                type="STRING",
                required=None,
                default=None,
                extensions=None,
                schema_=None,
            ),
            VellumVariable(
                id=str(first_call_input_id_2),
                key="chat_history",
                type="JSON",
                required=None,
                default=None,
                extensions=None,
                schema_=None,
            ),
        ],
        "parameters": DEFAULT_PROMPT_PARAMETERS,
        "blocks": [
            ChatMessagePromptBlock(
                block_type="CHAT_MESSAGE",
                state=None,
                cache_config=None,
                chat_role="SYSTEM",
                chat_source=None,
                chat_message_unterminated=None,
                blocks=[
                    RichTextPromptBlock(
                        block_type="RICH_TEXT",
                        state=None,
                        cache_config=None,
                        blocks=[
                            PlainTextPromptBlock(
                                block_type="PLAIN_TEXT",
                                state=None,
                                cache_config=None,
                                text="You are a helpful assistant with access to slow tools.",
                            )
                        ],
                    )
                ],
            ),
            ChatMessagePromptBlock(
                block_type="CHAT_MESSAGE",
                state=None,
                cache_config=None,
                chat_role="USER",
                chat_source=None,
                chat_message_unterminated=None,
                blocks=[
                    RichTextPromptBlock(
                        block_type="RICH_TEXT",
                        state=None,
                        cache_config=None,
                        blocks=[
                            VariablePromptBlock(
                                block_type="VARIABLE", state=None, cache_config=None, input_variable="question"
                            )
                        ],
                    )
                ],
            ),
            VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
        ],
        "settings": None,
        "functions": [
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="slow_tool_one",
                description="A tool that takes 0.5 seconds to execute.",
                parameters={"type": "object", "properties": {}, "required": []},
                inputs=None,
                forced=None,
                strict=None,
            ),
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="slow_tool_two",
                description="A tool that takes 0.5 seconds to execute.",
                parameters={"type": "object", "properties": {}, "required": []},
                inputs=None,
                forced=None,
                strict=None,
            ),
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="slow_tool_three_workflow",
                description="A subworkflow that takes 0.5 seconds to execute.",
                parameters={"type": "object", "properties": {}, "required": []},
                inputs=None,
                forced=None,
                strict=None,
            ),
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="slow_tool_four",
                description="A tool that should NOT be called in the test.",
                parameters={"type": "object", "properties": {}, "required": []},
                inputs=None,
                forced=None,
                strict=None,
            ),
        ],
        "expand_meta": AdHocExpandMeta(cost=None, model_name=None, usage=None, finish_reason=True),
        "request_options": mock.ANY,
    }


def test_parallel_stream(vellum_adhoc_prompt_client, vellum_client):
    """
    Test that parallel_tool_calls=True executes tools in parallel and only routes to called tools.
    """

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            # First call returns function calls for 3 tools (not 4)
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        name="slow_tool_one",
                        arguments={},
                        id="call_1",
                    ),
                ),
                FunctionCallVellumValue(
                    value=FunctionCall(
                        name="slow_tool_two",
                        arguments={},
                        id="call_2",
                    ),
                ),
                FunctionCallVellumValue(
                    value=FunctionCall(
                        name="slow_tool_three_workflow",
                        arguments={},
                        id="call_3",
                    ),
                ),
            ]
        else:
            # Second call returns final text
            expected_outputs = [
                StringVellumValue(
                    value="All tools executed successfully.",
                )
            ]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    # GIVEN a workflow with parallel_tool_calls=True
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events
    workflow = ToolCallingNodeParallelExecutionEnabledWorkflow()

    # WHEN the workflow is streamed and we measure time
    start_time = time.time()
    all_events = list(workflow.stream(event_filter=all_workflow_event_filter))
    end_time = time.time()
    execution_time = end_time - start_time

    # THEN the workflow completes successfully
    terminal_event = all_events[-1]
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND only the 3 called tools have node events (not slow_tool_four)
    node_initiated = [e for e in all_events if e.name == "node.execution.initiated"]
    node_names = [e.node_definition.__name__ for e in node_initiated]  # type: ignore[union-attr]

    called_tool_patterns = ["FunctionNode_slow_tool_one", "FunctionNode_slow_tool_two", "SlowToolThreeWorkflow"]
    for pattern in called_tool_patterns:
        matching = [name for name in node_names if pattern in name]
        assert len(matching) > 0, f"Expected to find node with pattern {pattern} in events"

    # AND slow_tool_four should NOT have events
    for node_name in node_names:
        assert "slow_tool_four" not in node_name, f"slow_tool_four should not have events, found {node_name}"

    # AND execution completes in < 0.8s (parallel: ~0.5s, sequential would be ~1.5s)
    assert execution_time < 0.8, (
        f"Expected parallel execution to complete in < 0.8s, but took {execution_time:.2f}s. "
        "This suggests tools are running sequentially instead of in parallel."
    )
