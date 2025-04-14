from vellum import TestSuiteRunMetricNumberOutput
from vellum.client.types.chat_history_input import ChatHistoryInput
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.json_input import JsonInput
from vellum.client.types.metric_definition_execution import MetricDefinitionExecution
from vellum.client.types.number_input import NumberInput
from vellum.client.types.string_input import StringInput
from vellum.workflows.nodes.displayable.guardrail_node.node import GuardrailNode


def test_guardrail_node__inputs(vellum_client):
    """Test that GuardrailNode correctly handles inputs."""

    # GIVEN a Guardrail Node with inputs
    class MyGuard(GuardrailNode):
        metric_definition = "example_metric_definition"
        metric_inputs = {
            "a_string": "hello",
            "a_chat_history": [ChatMessage(role="USER", text="Hello, how are you?")],
            "a_dict": {"foo": "bar"},
            "a_int": 42,
            "a_float": 3.14,
        }

    vellum_client.metric_definitions.execute_metric_definition.return_value = MetricDefinitionExecution(
        outputs=[
            TestSuiteRunMetricNumberOutput(
                name="score",
                value=1.0,
            ),
        ],
    )

    # WHEN the node is run
    MyGuard().run()

    # THEN the metric_definitions.execute_metric_definition method should be called with the correct inputs
    mock_api = vellum_client.metric_definitions.execute_metric_definition
    assert mock_api.call_count == 1

    assert mock_api.call_args.kwargs["inputs"] == [
        StringInput(name="a_string", type="STRING", value="hello"),
        ChatHistoryInput(
            name="a_chat_history", type="CHAT_HISTORY", value=[ChatMessage(role="USER", text="Hello, how are you?")]
        ),
        JsonInput(name="a_dict", type="JSON", value={"foo": "bar"}),
        NumberInput(name="a_int", type="NUMBER", value=42.0),
        NumberInput(name="a_float", type="NUMBER", value=3.14),
    ]
    assert len(mock_api.call_args.kwargs["inputs"]) == 5
