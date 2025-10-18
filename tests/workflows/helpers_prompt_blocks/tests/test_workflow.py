from unittest import mock
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    AdHocExecutePromptEvent,
    AdHocExpandMeta,
    ChatMessagePromptBlock,
    FulfilledAdHocExecutePromptEvent,
    InitiatedAdHocExecutePromptEvent,
    PlainTextPromptBlock,
    PromptOutput,
    PromptRequestStringInput,
    RichTextPromptBlock,
    StringVellumValue,
    VellumVariable,
)
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS

from tests.workflows.helpers_prompt_blocks.workflow import WorkflowInputs, WorkflowWithPromptBlockHelpers


def test_autocasting_blocks_compile_to_correct_api_schema(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """Test that SystemMessage and UserMessage autocast to correct ChatMessagePromptBlock API schema"""

    workflow = WorkflowWithPromptBlockHelpers()

    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="The item is blue."),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[AdHocExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[AdHocExecutePromptEvent] = [
            InitiatedAdHocExecutePromptEvent(execution_id=execution_id),
            FulfilledAdHocExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    expected_input_variable_id = uuid4_generator()

    # WHEN we run the workflow
    terminal_event = workflow.run(inputs=WorkflowInputs(user_query="What color is my car?"))

    assert terminal_event.name == "workflow.execution.fulfilled"

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.assert_called_once_with(
        ml_model="gpt-4o",
        input_values=[
            PromptRequestStringInput(
                key="user_query",
                type="STRING",
                value="What color is my car?",
            ),
        ],
        input_variables=[
            VellumVariable(
                id=str(expected_input_variable_id),
                key="user_query",
                type="STRING",
            ),
        ],
        parameters=DEFAULT_PROMPT_PARAMETERS,
        blocks=[
            ChatMessagePromptBlock(
                chat_role="SYSTEM",
                blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text="What color is the item?")])],
            ),
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(blocks=[PlainTextPromptBlock(text="Here is the user query: {{user_query}}")])
                ],
            ),
        ],
        expand_meta=AdHocExpandMeta(finish_reason=True),
        functions=None,
        request_options=mock.ANY,
        settings=None,
    )
