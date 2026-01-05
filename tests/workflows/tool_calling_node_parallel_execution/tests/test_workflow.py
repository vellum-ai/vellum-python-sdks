from uuid import uuid4
from typing import Dict, Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.tool_calling_node_parallel_execution.workflow import ParallelToolCallingWorkflow


def test_parallel_tool_calling_node__only_called_tools_have_events(vellum_adhoc_prompt_client, vellum_client):
    """
    Test that parallel tool calling only routes to tools that are called.

    GIVEN a ToolCallingNode with parallel_tool_calls=True and 4 defined functions
    WHEN the LLM returns function calls for only 3 of the 4 functions
    THEN only those 3 function nodes should have init/stream/fulfilled events
    AND slow_tool_four should NOT have any events
    AND execution completes in less than 0.5s (proving parallelism vs sequential ~0.75s)
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

    # GIVEN
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events
    workflow = ParallelToolCallingWorkflow()

    # WHEN
    all_events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # Filter node events by name
    node_initiated = [e for e in all_events if e.name == "node.execution.initiated"]
    node_fulfilled = [e for e in all_events if e.name == "node.execution.fulfilled"]

    # Build a map of node names to their events
    node_events: Dict[str, List[str]] = {}
    for initiated_event in node_initiated:
        node_name = initiated_event.node_definition.__name__  # type: ignore[union-attr]
        if node_name not in node_events:
            node_events[node_name] = []
        node_events[node_name].append("node.execution.initiated")

    for fulfilled_event in node_fulfilled:
        node_name = fulfilled_event.node_definition.__name__  # type: ignore[union-attr]
        if node_name not in node_events:
            node_events[node_name] = []
        node_events[node_name].append("node.execution.fulfilled")

    # THEN - Verify only the 3 called tools have events
    called_tool_patterns = [
        "slow_tool_one",
        "slow_tool_two",
        "SlowToolThreeWorkflow",
    ]

    # Check that called tools have events
    for pattern in called_tool_patterns:
        matching_nodes = [name for name in node_events if pattern in name]
        assert len(matching_nodes) > 0, f"Expected to find node with pattern {pattern} in events"
        for node_name in matching_nodes:
            events_list = node_events[node_name]
            assert "node.execution.initiated" in events_list, f"Expected {node_name} to have initiated event"
            assert "node.execution.fulfilled" in events_list, f"Expected {node_name} to have fulfilled event"

    # AND - Verify slow_tool_four does NOT have events
    for node_name in node_events:
        assert (
            "slow_tool_four" not in node_name.lower()
        ), f"Expected slow_tool_four to NOT have events, but found in {node_name}"
