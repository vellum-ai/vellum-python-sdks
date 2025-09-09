from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.none_access_expression.workflow import Workflow


def test_run_workflow(vellum_adhoc_prompt_client):
    # GIVEN a workflow that has a node referencing an optional input
    expected_outputs: List[PromptOutput] = [StringVellumValue(value="hello")]

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(execution_id=execution_id, outputs=expected_outputs),
        ]
        yield from events

    # AND the mock is set up to return our events to avoid real API calls
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    workflow = Workflow()
    terminal_event = workflow.run()

    # THEN the workflow should be rejected due to accessing a field on None
    assert terminal_event.name == "workflow.execution.rejected", terminal_event
    assert "Cannot get field message from None" in str(terminal_event)
