import pytest
import json
from typing import List, Union

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json


def test_templating_node__dict_output():
    # GIVEN a templating node with a dict input that just returns it
    class TemplateNode(TemplatingNode):
        template = "{{ data }}"
        inputs = {
            "data": {
                "key": "value",
            }
        }

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the output is json serializable
    # https://app.shortcut.com/vellum/story/6132
    dump: str = outputs.result  # type: ignore[assignment]
    assert json.loads(dump) == {"key": "value"}


def test_templating_node__int_output():
    # GIVEN a templating node that outputs an integer
    class IntTemplateNode(TemplatingNode[BaseState, int]):
        template = "{{ data }}"
        inputs = {
            "data": 42,
        }

    # WHEN the node is run
    node = IntTemplateNode()
    outputs = node.run()

    # THEN the output is the expected integer
    assert outputs.result == 42


def test_templating_node__float_output():
    # GIVEN a templating node that outputs a float
    class FloatTemplateNode(TemplatingNode[BaseState, float]):
        template = "{{ data }}"
        inputs = {
            "data": 42.5,
        }

    # WHEN the node is run
    node = FloatTemplateNode()
    outputs = node.run()

    # THEN the output is the expected float
    assert outputs.result == 42.5


def test_templating_node__bool_output():
    # GIVEN a templating node that outputs a bool
    class BoolTemplateNode(TemplatingNode[BaseState, bool]):
        template = "{{ data }}"
        inputs = {
            "data": True,
        }

    # WHEN the node is run
    node = BoolTemplateNode()
    outputs = node.run()

    # THEN the output is the expected bool
    assert outputs.result is True


def test_templating_node__json_output():
    # GIVEN a templating node that outputs JSON
    class JSONTemplateNode(TemplatingNode[BaseState, Json]):
        template = "{{ data }}"
        inputs = {
            "data": {"key": "value"},
        }

    # WHEN the node is run
    node = JSONTemplateNode()
    outputs = node.run()

    # THEN the output is the expected JSON
    assert outputs.result == {"key": "value"}


def test_templating_node__execution_count_reference():
    # GIVEN a random node
    class OtherNode(BaseNode):
        pass

    # AND a templating node that references the execution count of the random node
    class TemplateNode(TemplatingNode):
        template = "{{ total }}"
        inputs = {
            "total": OtherNode.Execution.count,
        }

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the output is just the total
    assert outputs.result == "0"


def test_templating_node__pydantic_to_json():
    # GIVEN a templating node that uses tojson on a pydantic model
    class JSONTemplateNode(TemplatingNode[BaseState, Json]):
        template = "{{ function_call | tojson }}"
        inputs = {
            "function_call": FunctionCall(name="test", arguments={"key": "value"}),
        }

    # WHEN the node is run
    node = JSONTemplateNode()
    outputs = node.run()

    # THEN the output is the expected JSON
    assert outputs.result == {"name": "test", "arguments": {"key": "value"}, "id": None}


def test_templating_node__chat_history_output():
    # GIVEN a templating node that outputs a chat history
    class ChatHistoryTemplateNode(TemplatingNode[BaseState, List[ChatMessage]]):
        template = '[{"role": "USER", "text": "Hello"}]'
        inputs = {}

    # WHEN the node is run
    node = ChatHistoryTemplateNode()
    outputs = node.run()

    # THEN the output is the expected chat history
    assert outputs.result == [ChatMessage(role="USER", text="Hello")]


def test_templating_node__function_call_output():
    # GIVEN a templating node that outputs a function call
    class FunctionCallTemplateNode(TemplatingNode[BaseState, FunctionCall]):
        template = '{"name": "test", "arguments": {"key": "value"}}'
        inputs = {}

    # WHEN the node is run
    node = FunctionCallTemplateNode()
    outputs = node.run()

    # THEN the output is the expected function call
    assert outputs.result == FunctionCall(name="test", arguments={"key": "value"})


def test_templating_node__blank_json_input():
    """Test that templating node properly handles blank JSON input."""

    # GIVEN a templating node that tries to parse blank JSON
    class BlankJsonTemplateNode(TemplatingNode[BaseState, Json]):
        template = "{{ json.loads(data) }}"
        inputs = {
            "data": "",  # Blank input
        }

    # WHEN the node is run
    node = BlankJsonTemplateNode()

    # THEN it should raise an appropriate error
    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert "Unable to render jinja template:\nCannot run json.loads() on empty input" in str(exc_info.value)


def test_templating_node__union_float_int_output():
    # GIVEN a templating node that outputs either a float or an int
    class UnionTemplateNode(TemplatingNode[BaseState, Union[float, int]]):
        template = """{{ obj[\"score\"] | float }}"""
        inputs = {
            "obj": {"score": 42.5},
        }

    # WHEN the node is run
    node = UnionTemplateNode()
    outputs = node.run()

    # THEN it should correctly parse as a float
    assert outputs.result == 42.5


def test_templating_node__replace_filter():
    # GIVEN a templating node that outputs a complex object
    class ReplaceFilterTemplateNode(TemplatingNode[BaseState, Json]):
        template = """{{- prompt_outputs | selectattr(\'type\', \'equalto\', \'FUNCTION_CALL\') \
        | list | replace(\"\\n\",\",\") -}}"""
        inputs = {
            "prompt_outputs": [FunctionCallVellumValue(value=FunctionCall(name="test", arguments={"key": "value"}))]
        }

    # WHEN the node is run
    node = ReplaceFilterTemplateNode()
    outputs = node.run()

    # THEN the output is the expected JSON
    assert outputs.result == [
        {
            "type": "FUNCTION_CALL",
            "value": {
                "name": "test",
                "arguments": {"key": "value"},
                "id": None,
            },
        }
    ]


def test_templating_node__last_chat_message():
    # GIVEN a templating node that outputs a complex object
    class LastChatMessageTemplateNode(TemplatingNode[BaseState, List[ChatMessage]]):
        template = """{{ chat_history[:-1] }}"""
        inputs = {"chat_history": [ChatMessage(role="USER", text="Hello"), ChatMessage(role="ASSISTANT", text="World")]}

    # WHEN the node is run
    node = LastChatMessageTemplateNode()
    outputs = node.run()

    # THEN the output is the expected JSON
    assert outputs.result == [ChatMessage(role="USER", text="Hello")]


def test_templating_node__function_call_value_input():
    # GIVEN a templating node that receives a FunctionCallVellumValue
    class FunctionCallTemplateNode(TemplatingNode[BaseState, FunctionCall]):
        template = """{{ function_call }}"""
        inputs = {
            "function_call": FunctionCallVellumValue(
                type="FUNCTION_CALL",
                value=FunctionCall(name="test_function", arguments={"key": "value"}, id="test_id", state="FULFILLED"),
            )
        }

    # WHEN the node is run
    node = FunctionCallTemplateNode()
    outputs = node.run()

    # THEN the output is the expected function call
    assert outputs.result == FunctionCall(
        name="test_function", arguments={"key": "value"}, id="test_id", state="FULFILLED"
    )


def test_templating_node__function_call_as_json():
    # GIVEN a node that receives a FunctionCallVellumValue but outputs as Json
    class JsonOutputNode(TemplatingNode[BaseState, Json]):
        template = """{{ function_call }}"""
        inputs = {
            "function_call": FunctionCallVellumValue(
                type="FUNCTION_CALL",
                value=FunctionCall(name="test_function", arguments={"key": "value"}, id="test_id", state="FULFILLED"),
            )
        }

    # WHEN the node is run
    node = JsonOutputNode()
    outputs = node.run()

    # THEN we get just the FunctionCall data as JSON
    assert outputs.result == {
        "name": "test_function",
        "arguments": {"key": "value"},
        "id": "test_id",
        "state": "FULFILLED",
    }

    # AND we can access fields directly
    assert outputs.result["arguments"] == {"key": "value"}
    assert outputs.result["name"] == "test_function"


def test_templating_node__empty_string_to_list():
    """Test that an empty string output with list output type casts to an empty array."""

    # GIVEN a templating node that outputs an empty string but has List output type
    class EmptyStringToListTemplateNode(TemplatingNode[BaseState, List[str]]):
        template = """{{ "" }}"""
        inputs = {}

    # WHEN the node is run
    node = EmptyStringToListTemplateNode()
    outputs = node.run()

    # THEN the output should be an empty list, not raise an exception
    assert outputs.result == []


def test_api_error_templating_node():
    class UndefinedTemplatingNode(TemplatingNode[BaseState, str]):
        template = """{{ foo | tojson }}"""
        inputs = {
            "bar": "bar",
            # foo is not define
        }

    # GIVEN a templating node with an undefined value
    node = UndefinedTemplatingNode()

    # WHEN the node is run
    outputs = node.run()

    # THEN the output should be empty string
    assert outputs.result == ""


def test_templating_node__string_value_access():
    # GIVEN a templating node that accesses string value
    class TemplateNode(TemplatingNode[BaseState, str]):
        template = "{{ text_input.value }}"
        inputs = {"text_input": "hello world"}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the value is accessible
    assert outputs.result == "hello world"


def test_templating_node__string_type_access():
    # GIVEN a templating node that accesses string type
    class TemplateNode(TemplatingNode[BaseState, str]):
        template = "{{ text_input.type }}"
        inputs = {"text_input": "hello world"}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the type is accessible
    assert outputs.result == "STRING"


def test_templating_node__function_call_value_access():
    # GIVEN a templating node that accesses function call value
    class TemplateNode(TemplatingNode[BaseState, str]):
        template = "{{ func.value.name }}"
        inputs = {"func": FunctionCall(name="test_function", arguments={"key": "value"})}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the function name is accessible
    assert outputs.result == "test_function"


def test_templating_node__function_call_type_access():
    # GIVEN a templating node that accesses function call type
    class TemplateNode(TemplatingNode[BaseState, str]):
        template = "{{ func.type }}"
        inputs = {"func": FunctionCall(name="test_function", arguments={"key": "value"})}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the function type is accessible
    assert outputs.result == "FUNCTION_CALL"


def test_templating_node__array_item_value_access():
    # GIVEN a templating node that accesses array item value
    class TemplateNode(TemplatingNode[BaseState, str]):
        template = "{{ items[0].value }}"
        inputs = {"items": ["apple"]}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the array item value is accessible
    assert outputs.result == "apple"


def test_templating_node__dict_value_access():
    # GIVEN a templating node that accesses dict value
    class TemplateNode(TemplatingNode[BaseState, Json]):
        template = "{{ data.value }}"
        inputs = {"data": {"name": "test", "score": 42}}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the dict returns itself as value
    assert outputs.result == {"name": "test", "score": 42}


def test_templating_node__list_value_access():
    # GIVEN a templating node that accesses list value
    class TemplateNode(TemplatingNode[BaseState, Json]):
        template = "{{ items.value }}"
        inputs = {"items": ["item1", "item2", "item3"]}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN the list returns itself as value
    assert outputs.result == ["item1", "item2", "item3"]


def test_templating_node__nested_dict_access():
    # GIVEN a templating node with nested dict access
    class TemplateNode(TemplatingNode[BaseState, str]):
        template = "{{ data.user.name }}"
        inputs = {"data": {"user": {"name": "John Doe", "age": 30}, "status": "active"}}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN nested properties are accessible
    assert outputs.result == "John Doe"


def test_templating_node__list_iteration_wrapper_access():
    # GIVEN a templating node that iterates over list with wrapper access
    class TemplateNode(TemplatingNode[BaseState, str]):
        template = "{% for item in items %}{{ item.value }}{% if not loop.last %},{% endif %}{% endfor %}"
        inputs = {"items": ["apple", "banana", "cherry"]}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN list iteration with wrapper access works
    assert outputs.result == "apple,banana,cherry"


def test_templating_node__conditional_type_checking():
    # GIVEN a templating node with conditional type checking
    class TemplateNode(TemplatingNode[BaseState, str]):
        template = "{% if input.type == 'STRING' %}{{ input.value }}{% else %}unknown{% endif %}"
        inputs = {"input": "test string"}

    # WHEN the node is run
    node = TemplateNode()
    outputs = node.run()

    # THEN conditional type checking works
    assert outputs.result == "test string"
