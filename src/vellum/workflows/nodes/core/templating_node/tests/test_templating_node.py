import json

from vellum.client.types.function_call import FunctionCall
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
