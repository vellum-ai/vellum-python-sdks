from dataclasses import dataclass
from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_request_json_input import PromptRequestJsonInput
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.nodes.displayable.bases.inline_prompt_node.node import BaseInlinePromptNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode


def test_inline_prompt_node__json_inputs(vellum_adhoc_prompt_client):
    # GIVEN a prompt node with various inputs
    @dataclass
    class MyDataClass:
        hello: str

    class MyPydantic(UniversalBaseModel):
        example: str

    class MyNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []
        prompt_inputs = {
            "a_dict": {"foo": "bar"},
            "a_list": [1, 2, 3],
            "a_dataclass": MyDataClass(hello="world"),
            "a_pydantic": MyPydantic(example="example"),
        }

    # AND a known response from invoking an inline prompt
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Test"),
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

    # WHEN the node is run
    list(MyNode().run())

    # THEN the prompt is executed with the correct inputs
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1
    assert mock_api.call_args.kwargs["input_values"] == [
        PromptRequestJsonInput(key="a_dict", type="JSON", value={"foo": "bar"}),
        PromptRequestJsonInput(key="a_list", type="JSON", value=[1, 2, 3]),
        PromptRequestJsonInput(key="a_dataclass", type="JSON", value={"hello": "world"}),
        PromptRequestJsonInput(key="a_pydantic", type="JSON", value={"example": "example"}),
    ]
    assert len(mock_api.call_args.kwargs["input_variables"]) == 4


def test_inline_prompt_node__function_definitions(vellum_adhoc_prompt_client):
    # GIVEN a function definition
    def my_function(foo: str, bar: int) -> None:
        pass

    # AND a prompt node with a accepting that function definition
    class MyNode(BaseInlinePromptNode):
        ml_model = "gpt-4o"
        functions = [my_function]
        prompt_inputs = {}
        blocks = []

    # AND a known response from invoking an inline prompt
    expected_outputs: List[PromptOutput] = [
        FunctionCallVellumValue(value=FunctionCall(name="my_function", arguments={"foo": "hello", "bar": 1})),
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

    # WHEN the node is run
    list(MyNode().run())

    # THEN the prompt is executed with the correct inputs
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1
    assert mock_api.call_args.kwargs["functions"] == [
        FunctionDefinition(
            name="my_function",
            parameters={
                "type": "object",
                "properties": {
                    "foo": {"type": "string"},
                    "bar": {"type": "integer"},
                },
                "required": ["foo", "bar"],
            },
        ),
    ]
