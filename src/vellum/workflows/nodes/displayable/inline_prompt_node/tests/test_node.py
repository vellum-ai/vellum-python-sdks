from dataclasses import dataclass

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode


def test_inline_prompt_node__json_inputs(vellum_adhoc_prompt_client):
    # GIVEN a prompt node with various inputs
    @dataclass
    class MyDataClass:
        hello: str

    class MyPydantic(UniversalBaseModel):
        example: str

    class MyNode(InlinePromptNode):
        prompt_inputs = {
            "a_dict": {"foo": "bar"},
            "a_list": [1, 2, 3],
            "a_dataclass": MyDataClass(hello="world"),
            "a_pydantic": MyPydantic(example="example"),
        }

    # WHEN the node is run
    list(MyNode().run())

    # THEN the prompt is executed with the correct inputs
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1
    assert mock_api.call_args[0]["input_values"] == {
        "a_dict": {"type": "JSON", "value": {"foo": "bar"}},
        "a_list": {"type": "JSON", "value": [1, 2, 3]},
        "a_dataclass": {"type": "JSON", "value": {"hello": "world"}},
        "a_pydantic": {"type": "JSON", "value": {"example": "example"}},
    }
    assert len(mock_api.call_args[0]["input_variables"]) == 4
