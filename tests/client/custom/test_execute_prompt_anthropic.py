from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    ChatMessagePromptBlock,
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    InitiatedExecutePromptEvent,
    PromptOutput,
    PromptParameters,
    RichTextPromptBlock,
    StringVellumValue,
    Vellum,
)


def test_execute_prompt_anthropic__rich_text_blocks(vellum_adhoc_prompt_client):
    """
    Tests that execute_prompt with Anthropic sends the correct request structure
    with RICH_TEXT blocks in CHAT_MESSAGE blocks.
    """

    test_blocks = [
        ChatMessagePromptBlock(
            blocks=[
                RichTextPromptBlock(
                    blocks=[],
                ),
            ],
            chat_role="SYSTEM",
        ),
    ]

    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Test response from Anthropic"),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    client = Vellum(api_key="test-key")
    client.ad_hoc = vellum_adhoc_prompt_client

    list(
        client.ad_hoc.adhoc_execute_prompt_stream(
            ml_model="claude-3-5-sonnet-20241022",
            blocks=test_blocks,
            input_values=[],
            input_variables=[],
            parameters=PromptParameters(),
        )
    )

    # THEN the request should have been made with the correct block structure
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1

    # AND the blocks should match the expected structure
    call_kwargs = mock_api.call_args.kwargs
    assert "blocks" in call_kwargs
    assert len(call_kwargs["blocks"]) == 1

    chat_message_block = call_kwargs["blocks"][0]
    assert chat_message_block.block_type == "CHAT_MESSAGE"
    assert chat_message_block.chat_role == "SYSTEM"

    assert len(chat_message_block.blocks) == 1
    rich_text_block = chat_message_block.blocks[0]
    assert rich_text_block.block_type == "RICH_TEXT"
    assert rich_text_block.blocks == []
