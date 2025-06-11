from unittest import mock
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    AdHocExecutePromptEvent,
    ChatMessagePromptBlock,
    FulfilledAdHocExecutePromptEvent,
    InitiatedAdHocExecutePromptEvent,
    JinjaPromptBlock,
    PromptOutput,
    PromptRequestStringInput,
    StringInput,
    StringVellumValue,
    TestSuiteRunMetricNumberOutput,
    VellumVariable,
)
from vellum.client.types.metric_definition_execution import MetricDefinitionExecution
from vellum.client.types.prompt_settings import PromptSettings
from vellum.workflows.constants import LATEST_RELEASE_TAG
from vellum.workflows.nodes.displayable.bases.inline_prompt_node.constants import DEFAULT_PROMPT_PARAMETERS

from tests.workflows.basic_retry_node_annotation.workflow_with_retry_and_guardrail_nodes import (
    WorkflowInputs,
    WorkflowWithRetryAndGuardrailNodes,
)


def test_workflow_with_two_nodes__happy_path(vellum_client, vellum_adhoc_prompt_client, mock_uuid4_generator):
    # GIVEN a workflow with a retry-wrapped prompt node and a guardrail node
    workflow = WorkflowWithRetryAndGuardrailNodes()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="My favorite city is NYC."),
    ]

    def generate_prompt_events(*_args: Any, **_kwargs: Any) -> Iterator[AdHocExecutePromptEvent]:
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

    # AND we know what the Guardrail Node will respond with
    mock_metric_execution = MetricDefinitionExecution(
        outputs=[
            TestSuiteRunMetricNumberOutput(
                name="score",
                value=0.8,
            )
        ],
    )
    vellum_client.metric_definitions.execute_metric_definition.return_value = mock_metric_execution

    # WHEN the workflow is run
    terminal_event = workflow.run(inputs=WorkflowInputs(noun="city"))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the expected value
    assert terminal_event.outputs == {"final_value": 0.8}

    # AND we should have invoked the prompt with the expected inputs
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.assert_called_with(
        ml_model="gpt-4o",
        input_values=[
            PromptRequestStringInput(
                key="noun",
                type="STRING",
                value="city",
            ),
        ],
        input_variables=[
            VellumVariable(
                id=str(expected_input_variable_id),
                key="noun",
                type="STRING",
            ),
        ],
        parameters=DEFAULT_PROMPT_PARAMETERS,
        blocks=[
            ChatMessagePromptBlock(
                chat_role="SYSTEM",
                blocks=[
                    JinjaPromptBlock(
                        block_type="JINJA",
                        template="What's your favorite {{noun}}?",
                    ),
                ],
            ),
        ],
        expand_meta=None,
        functions=None,
        request_options=mock.ANY,
        settings=PromptSettings(timeout=1, stream_enabled=True),
    )

    # AND we should have invoked the metric definition with the expected inputs
    vellum_client.metric_definitions.execute_metric_definition.assert_called_with(
        "e0869d84-1bb6-4e8c-85ad-67fd28ff8f59",
        inputs=[
            StringInput(name="actual", value="My favorite city is NYC."),
        ],
        release_tag=LATEST_RELEASE_TAG,
        request_options=None,
    )
