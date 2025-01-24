import pytest
import enum

from pydantic import BaseModel

from vellum.client.types.chat_history_vellum_value import ChatHistoryVellumValue
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.error_vellum_value import ErrorVellumValue
from vellum.client.types.json_vellum_value import JsonVellumValue
from vellum.client.types.number_vellum_value import NumberVellumValue
from vellum.client.types.search_result import SearchResult
from vellum.client.types.search_result_document import SearchResultDocument
from vellum.client.types.search_results_vellum_value import SearchResultsVellumValue
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.string_vellum_value_request import StringVellumValueRequest
from vellum.client.types.vellum_error import VellumError
from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value, primitive_to_vellum_value_request


class MockEnum(enum.Enum):
    FOO = "foo"


class RandomPydanticModel(BaseModel):
    foo: str


@pytest.mark.parametrize(
    ["value", "expected_output"],
    [
        ("hello", StringVellumValue(value="hello")),
        (MockEnum.FOO, StringVellumValue(value="foo")),
        (1, NumberVellumValue(value=1)),
        (1.0, NumberVellumValue(value=1.0)),
        (
            [ChatMessage(role="USER", text="hello")],
            ChatHistoryVellumValue(value=[ChatMessage(role="USER", text="hello")]),
        ),
        (
            [
                SearchResult(
                    text="Search query",
                    score="0.0",
                    keywords=["keywords"],
                    document=SearchResultDocument(label="label"),
                )
            ],
            SearchResultsVellumValue(
                value=[
                    SearchResult(
                        text="Search query",
                        score="0.0",
                        keywords=["keywords"],
                        document=SearchResultDocument(label="label"),
                    )
                ]
            ),
        ),
        (StringVellumValue(value="hello"), StringVellumValue(value="hello")),
        (StringVellumValueRequest(value="hello"), StringVellumValueRequest(value="hello")),
        ({"foo": "bar"}, JsonVellumValue(value={"foo": "bar"})),
        (
            VellumError(message="hello", code="USER_DEFINED_ERROR"),
            ErrorVellumValue(value=VellumError(message="hello", code="USER_DEFINED_ERROR")),
        ),
        (
            WorkflowError(message="hello", code=WorkflowErrorCode.USER_DEFINED_ERROR),
            ErrorVellumValue(value=VellumError(message="hello", code="USER_DEFINED_ERROR")),
        ),
        (RandomPydanticModel(foo="bar"), JsonVellumValue(value={"foo": "bar"})),
    ],
)
def test_primitive_to_vellum_value(value, expected_output):
    assert primitive_to_vellum_value(value) == expected_output


def test_primitive_to_vellum_value_request():
    assert primitive_to_vellum_value_request("hello") == StringVellumValueRequest(value="hello")
