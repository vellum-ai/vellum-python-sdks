import time
from unittest import mock
from uuid import uuid4
from typing import Iterator

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

from tests.workflows.tool_calling_node_parallel_execution.workflow import ToolCallingNodeParallelExecutionWorkflow


def test_parallel_tool_execution_sequential_baseline(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Test that establishes the baseline timing for sequential tool execution.

    Currently, three tools that each take 0.5s should execute sequentially,
    taking approximately 1.5s total. This test will later be modified to
    verify parallel execution takes ~0.5s total.
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
                        id="call_slow_tool_three",
                        name="slow_tool_three",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            # Second LLM call returns final response
            expected_outputs = [StringVellumValue(value="All three slow tools executed successfully.")]

        events = [
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

    # AND the execution took approximately 1.5 seconds (sequential: 0.5 + 0.5 + 0.5)
    assert total_time >= 1.5, f"Expected >= 1.5s for sequential execution (0.5*3), got {total_time:.2f}s"

    # AND the chat history shows all three tools were executed sequentially
    chat_history = terminal_event.outputs.chat_history
    assert len(chat_history) == 5  # 1 function calls message + 3 function results + 1 final response

    assert chat_history[0].role == "ASSISTANT"  # First function call (all three)
    assert chat_history[1].role == "FUNCTION"  # First result
    assert chat_history[2].role == "FUNCTION"  # Second result
    assert chat_history[3].role == "FUNCTION"  # Third result
    assert chat_history[4].role == "ASSISTANT"  # Final response

    # Verify all three tools actually executed by checking their results in chat history
    function_results = [msg for msg in chat_history if msg.role == "FUNCTION"]
    assert len(function_results) == 3

    # Extract the tool results from the function messages
    expected_results = ["slow_tool_one_result", "slow_tool_two_result", "slow_tool_three_result"]
    actual_results = []
    for result_msg in function_results:
        actual_results.append(result_msg.content.value.strip('"'))

    assert set(actual_results) == set(expected_results)

    first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
    assert first_call.kwargs == {
        "ml_model": "gpt-4o-mini",
        "input_values": [
            PromptRequestStringInput(
                key="question", type="STRING", value="Execute all three slow tools and summarize the results."
            ),
            PromptRequestJsonInput(
                key="chat_history",
                type="JSON",
                value=[],
            ),
        ],
        "input_variables": [
            VellumVariable(
                id=str(first_call_input_id),
                key="question",
                type="STRING",
                required=None,
                default=None,
                extensions=None,
            ),
            VellumVariable(
                id=str(first_call_input_id_2),
                key="chat_history",
                type="JSON",
                required=None,
                default=None,
                extensions=None,
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
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
                forced=None,
                strict=None,
            ),
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="slow_tool_two",
                description="A tool that takes 0.5 seconds to execute.",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
                forced=None,
                strict=None,
            ),
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="slow_tool_three",
                description="A tool that takes 0.5 seconds to execute.",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
                forced=None,
                strict=None,
            ),
        ],
        "expand_meta": AdHocExpandMeta(finish_reason=True),
        "request_options": mock.ANY,
    }
