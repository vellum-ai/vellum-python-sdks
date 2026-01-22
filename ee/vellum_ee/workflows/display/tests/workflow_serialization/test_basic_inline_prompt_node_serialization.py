from typing import List

from deepdiff import DeepDiff

from vellum import ChatMessagePromptBlock, FunctionDefinition, JinjaPromptBlock
from vellum.client.types.chat_message import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_inline_prompt_node_with_functions.workflow import BasicInlinePromptWithFunctionsWorkflow


def test_serialize_workflow():
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicInlinePromptWithFunctionsWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1
    assert not DeepDiff(
        [
            {
                "id": "ceb5cc94-48ee-4968-b37a-421623a8f1ef",
                "key": "noun",
                "type": "STRING",
                "default": None,
                "required": True,
                "extensions": {"color": None},
                "schema": {"type": "string"},
            }
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {"id": "15a0ab89-8ed4-43b9-afa2-3c0b29d4dc3e", "key": "results", "type": "ARRAY"},
            {"id": "0ef1608e-1737-41cc-9b90-a8e124138f70", "key": "json", "type": "JSON"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND each node should be serialized correctly

    prompt_node = next(n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "InlinePromptNode")
    assert not DeepDiff(
        {
            "id": "f800ecab-fe14-498f-88cf-8f67b3f04338",
            "type": "PROMPT",
            "inputs": [
                {
                    "id": "15381676-75eb-4688-8ae1-7f9f937d6bb0",
                    "key": "noun",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "ceb5cc94-48ee-4968-b37a-421623a8f1ef"},
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "data": {
                "label": "Example Base Inline Prompt Node With Functions",
                "output_id": "71f6717e-31b5-478c-b204-9da91dfa6a29",
                "error_output_id": None,
                "array_output_id": "f5180d8d-89e4-479d-8baf-f6db8f9defa6",
                "source_handle_id": "6fad8947-ecce-498f-8160-46af26b75a81",
                "target_handle_id": "7040f290-6b61-4519-86f5-d004c38a6905",
                "variant": "INLINE",
                "exec_config": {
                    "parameters": {
                        "stop": [],
                        "temperature": 0.0,
                        "max_tokens": 4096,
                        "top_p": 1.0,
                        "top_k": 0,
                        "frequency_penalty": 0.0,
                        "presence_penalty": 0.0,
                        "logit_bias": None,
                        "custom_parameters": None,
                    },
                    "input_variables": [
                        {
                            "id": "15381676-75eb-4688-8ae1-7f9f937d6bb0",
                            "key": "noun",
                            "type": "STRING",
                        }
                    ],
                    "prompt_template_block_data": {
                        "version": 1,
                        "blocks": [
                            {
                                "block_type": "CHAT_MESSAGE",
                                "properties": {
                                    "chat_role": "SYSTEM",
                                    "chat_source": None,
                                    "chat_message_unterminated": False,
                                    "blocks": [
                                        {
                                            "block_type": "JINJA",
                                            "properties": {
                                                "template": "What's your favorite {{noun}}?",
                                                "template_type": "STRING",
                                            },
                                            "id": "9aa7793c-80a9-4321-b69a-5c0d819702d4",
                                            "cache_config": None,
                                            "state": "ENABLED",
                                        }
                                    ],
                                },
                                "id": "e8835fe3-f6c4-4140-8dda-cd455c2749ad",
                                "cache_config": None,
                                "state": "ENABLED",
                            },
                            {
                                "id": "d02e499e-8a37-47a0-bf29-d1ef418b64a6",
                                "block_type": "FUNCTION_DEFINITION",
                                "properties": {
                                    "function_name": "favorite_noun",
                                    "function_description": "Returns the favorite noun of the user",
                                    "function_parameters": {},
                                    "function_forced": None,
                                    "function_strict": None,
                                },
                            },
                        ],
                    },
                },
                "ml_model_name": "gpt-4o",
            },
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "name": "InlinePromptNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "inline_prompt_node", "node"],
            },
            "definition": {
                "name": "ExampleBaseInlinePromptNodeWithFunctions",
                "module": ["tests", "workflows", "basic_inline_prompt_node_with_functions", "workflow"],
            },
            "trigger": {
                "id": "7040f290-6b61-4519-86f5-d004c38a6905",
                "merge_behavior": "AWAIT_ANY",
            },
            "outputs": [
                {"id": "3170eef8-02ec-458d-b2f0-a916241227e4", "name": "json", "type": "JSON", "value": None},
                {"id": "71f6717e-31b5-478c-b204-9da91dfa6a29", "name": "text", "type": "STRING", "value": None},
                {"id": "f5180d8d-89e4-479d-8baf-f6db8f9defa6", "name": "results", "type": "ARRAY", "value": None},
            ],
            "ports": [{"id": "6fad8947-ecce-498f-8160-46af26b75a81", "name": "default", "type": "DEFAULT"}],
            "attributes": [
                {
                    "id": "7d5ff6a6-ff5f-4ed5-8ac6-d8138bf5f013",
                    "name": "ml_model",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "gpt-4o"}},
                },
                {
                    "id": "5fa00fe1-1b5d-4152-becf-88dec77d9225",
                    "name": "blocks",
                    "value": {
                        "type": "CONSTANT_VALUE",
                        "value": {
                            "type": "JSON",
                            "value": [
                                {
                                    "block_type": "CHAT_MESSAGE",
                                    "state": None,
                                    "cache_config": None,
                                    "chat_role": "SYSTEM",
                                    "chat_source": None,
                                    "chat_message_unterminated": None,
                                    "blocks": [
                                        {
                                            "block_type": "JINJA",
                                            "state": None,
                                            "cache_config": None,
                                            "template": "What's your favorite {{noun}}?",
                                        }
                                    ],
                                }
                            ],
                        },
                    },
                },
                {
                    "id": "51aceca7-ce5a-46c4-a52c-7a809b06cdd4",
                    "name": "prompt_inputs",
                    "value": {
                        "type": "DICTIONARY_REFERENCE",
                        "entries": [
                            {
                                "id": "cec57542-894a-4c2d-8aa3-3496dddbc519",
                                "key": "noun",
                                "value": {
                                    "type": "WORKFLOW_INPUT",
                                    "input_variable_id": "ceb5cc94-48ee-4968-b37a-421623a8f1ef",
                                },
                            }
                        ],
                    },
                },
                {
                    "id": "4ae711ff-fdac-4896-bba9-9a957a5d0329",
                    "name": "functions",
                    "value": {
                        "type": "CONSTANT_VALUE",
                        "value": {
                            "type": "JSON",
                            "value": [
                                {
                                    "state": None,
                                    "cache_config": None,
                                    "name": "favorite_noun",
                                    "description": "Returns the favorite noun of the user",
                                    "parameters": {},
                                    "inputs": None,
                                    "forced": None,
                                    "strict": None,
                                }
                            ],
                        },
                    },
                },
                {
                    "id": "36fee5be-69e0-48cb-8aff-db1fe22aed6f",
                    "name": "parameters",
                    "value": {
                        "type": "CONSTANT_VALUE",
                        "value": {
                            "type": "JSON",
                            "value": {
                                "stop": [],
                                "temperature": 0.0,
                                "max_tokens": 4096,
                                "top_p": 1.0,
                                "top_k": 0,
                                "frequency_penalty": 0.0,
                                "presence_penalty": 0.0,
                                "logit_bias": None,
                                "custom_parameters": None,
                            },
                        },
                    },
                },
            ],
        },
        prompt_node,
        ignore_order=True,
    )

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicInlinePromptWithFunctionsWorkflow",
        "module": ["tests", "workflows", "basic_inline_prompt_node_with_functions", "workflow"],
    }


def test_serialize_workflow_with_descriptor_functions():
    """Test that serialization handles BaseDescriptor instances in functions list."""

    class TestInputs(BaseInputs):
        noun: str

    class MockMCPClientNode(BaseNode):

        class Outputs(BaseNode.Outputs):
            tools: list[FunctionDefinition]

    class TestInlinePromptNodeWithDescriptorFunctions(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="SYSTEM",
                blocks=[JinjaPromptBlock(template="Test {{noun}}")],
            ),
        ]
        prompt_inputs = {"noun": TestInputs.noun}
        functions = MockMCPClientNode.Outputs.tools  # type: ignore

    class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
        graph = MockMCPClientNode >> TestInlinePromptNodeWithDescriptorFunctions

    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized: dict = workflow_display.serialize()

    prompt_nodes = [node for node in serialized["workflow_raw_data"]["nodes"] if node["type"] == "PROMPT"]
    assert len(prompt_nodes) == 1

    prompt_node = prompt_nodes[0]
    assert isinstance(prompt_node, dict)
    blocks = prompt_node["data"]["exec_config"]["prompt_template_block_data"]["blocks"]
    assert isinstance(blocks, list)

    function_blocks = [
        block for block in blocks if isinstance(block, dict) and block.get("block_type") == "FUNCTION_DEFINITION"
    ]
    assert len(function_blocks) == 0  # We don't serialize the legacy function blocks when dynamic

    assert "attributes" in prompt_node
    assert isinstance(prompt_node["attributes"], list)
    functions_attr = next(
        (attr for attr in prompt_node["attributes"] if isinstance(attr, dict) and attr["name"] == "functions"), None
    )
    assert isinstance(functions_attr, dict), "functions attribute should be present in serialized attributes"

    assert functions_attr["value"] == {
        "node_id": "483d3104-ce08-47fb-98ff-cb1813ab9885",
        "node_output_id": "c7ab8632-0cad-40e2-a49e-bf2731bb7f60",
        "type": "NODE_OUTPUT",
    }


def test_serialize_workflow_with_descriptor_blocks():
    """Test that serialization handles BaseDescriptor instances in blocks list."""

    class TestInputs(BaseInputs):
        noun: str

    class UpstreamNode(BaseNode):

        class Outputs(BaseNode.Outputs):
            results: list

        def run(self) -> Outputs:
            return self.Outputs(results=["test"])

    class TestInlinePromptNodeWithDescriptorBlocks(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = [UpstreamNode.Outputs.results[0]]  # type: ignore
        prompt_inputs = {"noun": TestInputs.noun}

    class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
        graph = UpstreamNode >> TestInlinePromptNodeWithDescriptorBlocks

    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized: dict = workflow_display.serialize()

    prompt_nodes = [node for node in serialized["workflow_raw_data"]["nodes"] if node["type"] == "PROMPT"]
    prompt_node = prompt_nodes[0]

    blocks = prompt_node["data"]["exec_config"]["prompt_template_block_data"]["blocks"]
    descriptor_blocks = [block for block in blocks if not isinstance(block, dict) or not block.get("block_type")]
    assert len(descriptor_blocks) == 0, "BaseDescriptor blocks should not appear in serialized blocks"

    blocks_attr = next((attr for attr in prompt_node["attributes"] if attr["name"] == "blocks"), None)
    assert blocks_attr is not None, "blocks attribute should be present when blocks contain BaseDescriptor"
    assert blocks_attr["value"]["type"] == "ARRAY_REFERENCE", "blocks attribute should be serialized as ARRAY_REFERENCE"
    assert blocks_attr["value"]["items"] == [
        {
            "type": "BINARY_EXPRESSION",
            "lhs": {
                "type": "NODE_OUTPUT",
                "node_id": str(UpstreamNode.__id__),
                "node_output_id": str(UpstreamNode.__output_ids__["results"]),
            },
            "operator": "accessField",
            "rhs": {
                "type": "CONSTANT_VALUE",
                "value": {
                    "type": "NUMBER",
                    "value": 0.0,
                },
            },
        }
    ]


def test_serialize_workflow_with_nested_descriptor_blocks():
    """Test that serialization handles BaseDescriptor instances nested in ChatMessageBlock.blocks."""

    class TestInputs(BaseInputs):
        noun: str

    class UpstreamNode(BaseNode):

        class Outputs(BaseNode.Outputs):
            results: list

        def run(self) -> Outputs:
            return self.Outputs(results=["test"])

    chat_block = ChatMessagePromptBlock(chat_role="SYSTEM", blocks=[JinjaPromptBlock(template="Hello")])

    class TestInlinePromptNodeWithNestedDescriptorBlocks(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = [chat_block]
        prompt_inputs = {"noun": TestInputs.noun}

    object.__setattr__(chat_block, "blocks", [UpstreamNode.Outputs.results[0]])

    class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
        graph = UpstreamNode >> TestInlinePromptNodeWithNestedDescriptorBlocks

    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized: dict = workflow_display.serialize()

    prompt_nodes = [node for node in serialized["workflow_raw_data"]["nodes"] if node["type"] == "PROMPT"]
    prompt_node = prompt_nodes[0]

    blocks = prompt_node["data"]["exec_config"]["prompt_template_block_data"]["blocks"]
    descriptor_blocks = [block for block in blocks if not isinstance(block, dict) or not block.get("block_type")]
    assert len(descriptor_blocks) == 0, "BaseDescriptor blocks should not appear in serialized blocks"

    blocks_attr = next((attr for attr in prompt_node["attributes"] if attr["name"] == "blocks"), None)
    assert blocks_attr is not None, "blocks attribute should be present when blocks contain nested BaseDescriptor"
    assert blocks_attr["value"]["type"] == "ARRAY_REFERENCE", "blocks attribute should be serialized as ARRAY_REFERENCE"
    assert blocks_attr["value"]["items"] == [
        {
            "entries": [
                {
                    "id": "d84963ba-9f9f-446a-8341-5e16fb81efea",
                    "key": "block_type",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "CHAT_MESSAGE"}},
                },
                {
                    "id": "cbe1cbe1-c40c-4479-9521-fdde77f38740",
                    "key": "state",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                },
                {
                    "id": "2aece7e1-a392-4744-9a8b-39e4c46583ea",
                    "key": "cache_config",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                },
                {
                    "id": "d4e3b6c5-fcb5-4348-b3f4-a9758d26ee84",
                    "key": "chat_role",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "SYSTEM"}},
                },
                {
                    "id": "4efd1012-d201-4946-b087-c8cde47dbdee",
                    "key": "chat_source",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                },
                {
                    "id": "fbe0f3a4-fedc-448d-92fa-b34485ef839c",
                    "key": "chat_message_unterminated",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                },
                {
                    "id": "f68bde51-e730-44d7-97a6-421d5d7b8e4d",
                    "key": "blocks",
                    "value": {
                        "items": [
                            {
                                "lhs": {
                                    "node_id": "e83d975b-3a41-4164-b644-b4e75ef60b98",
                                    "node_output_id": "ff10b7e3-1f60-43d8-bd6e-6843b2eb870e",
                                    "type": "NODE_OUTPUT",
                                },
                                "operator": "accessField",
                                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 0.0}},
                                "type": "BINARY_EXPRESSION",
                            }
                        ],
                        "type": "ARRAY_REFERENCE",
                    },
                },
            ],
            "definition": {
                "name": "ChatMessagePromptBlock",
                "module": ["vellum", "client", "types", "chat_message_prompt_block"],
            },
            "type": "DICTIONARY_REFERENCE",
        }
    ]


def test_inline_prompt_node__coalesce_expression_serialization():
    """
    Tests that prompt nodes can serialize coalesce expressions like State.chat_history.coalesce([]).
    """

    # GIVEN a custom state with chat_history
    class MyState(BaseState):
        chat_history: List[ChatMessage] = []

    # AND a prompt node that uses a coalesce expression as input
    class MyNode(InlinePromptNode[MyState]):
        ml_model = "gpt-4o"
        blocks = []
        prompt_inputs = {
            "chat_history": MyState.chat_history.coalesce([]),
        }

    class TestWorkflow(BaseWorkflow[BaseInputs, MyState]):
        graph = MyNode

    # WHEN the node is serialized
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized: dict = workflow_display.serialize()

    # THEN the prompt is serialized with the correct inputs
    prompt_nodes = [node for node in serialized["workflow_raw_data"]["nodes"] if node["type"] == "PROMPT"]
    prompt_node = prompt_nodes[0]

    prompt_inputs_attr = next((attr for attr in prompt_node["attributes"] if attr["name"] == "prompt_inputs"), None)
    assert prompt_inputs_attr
    assert prompt_inputs_attr["value"]["type"] == "DICTIONARY_REFERENCE"
    chat_history_entry = prompt_inputs_attr["value"]["entries"][0]

    assert chat_history_entry["key"] == "chat_history"
    assert chat_history_entry["value"]["type"] == "BINARY_EXPRESSION"
    assert chat_history_entry["value"]["operator"] == "coalesce"
    assert chat_history_entry["value"]["lhs"] == {
        "type": "WORKFLOW_STATE",
        "state_variable_id": "34dc3ea7-e44e-45ac-af42-8d765c4d3c00",
    }
    assert chat_history_entry["value"]["rhs"] == {
        "type": "CONSTANT_VALUE",
        "value": {
            "type": "JSON",
            "value": [],
        },
    }
