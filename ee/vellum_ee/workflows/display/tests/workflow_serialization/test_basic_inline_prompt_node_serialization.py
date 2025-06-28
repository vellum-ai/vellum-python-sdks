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
            }
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert not DeepDiff(
        [{"id": "15a0ab89-8ed4-43b9-afa2-3c0b29d4dc3e", "key": "results", "type": "JSON"}],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["edges"]) == 2
    assert len(workflow_raw_data["nodes"]) == 3

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "382842a3-0490-4dee-b87b-eef86766f07c",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "8294baa6-8bf4-4b54-a56b-407b64851b77"},
        "display_data": {"position": {"x": 0.0, "y": -50.0}},
        "base": None,
        "definition": None,
    }

    prompt_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "8450dd06-975a-41a4-a564-808ee8808fe6",
            "type": "PROMPT",
            "inputs": [
                {
                    "id": "f7fca55e-93e9-4009-9227-acf839c7990d",
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
                "output_id": "ead0ccb5-092f-4d9b-a9ec-5eb83d498188",
                "error_output_id": None,
                "array_output_id": "628df199-a049-40b9-a29b-a378edd759bb",
                "source_handle_id": "d4a097ab-e22d-42f1-b6bc-2ed96856377a",
                "target_handle_id": "c2dccecb-8a41-40a8-95af-325d3ab8bfe5",
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
                        {"id": "f7fca55e-93e9-4009-9227-acf839c7990d", "key": "noun", "type": "STRING"}
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
                                            "id": "467fe2b1-312b-40db-8869-9c6ada7c7077",
                                            "cache_config": None,
                                            "state": "ENABLED",
                                        }
                                    ],
                                },
                                "id": "1d1e117d-19dc-4282-b1e3-9534014fb6e5",
                                "cache_config": None,
                                "state": "ENABLED",
                            },
                            {
                                "id": "9b34f084-449d-423f-8691-37518b1ee9ca",
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
            "display_data": {"position": {"x": 200.0, "y": -50.0}},
            "base": {
                "name": "InlinePromptNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "inline_prompt_node", "node"],
            },
            "definition": {
                "name": "ExampleBaseInlinePromptNodeWithFunctions",
                "module": ["tests", "workflows", "basic_inline_prompt_node_with_functions", "workflow"],
            },
            "outputs": [
                {"id": "9557bd86-702d-4b45-b8c1-c3980bffe28f", "name": "json", "type": "JSON", "value": None},
                {"id": "ead0ccb5-092f-4d9b-a9ec-5eb83d498188", "name": "text", "type": "STRING", "value": None},
                {"id": "628df199-a049-40b9-a29b-a378edd759bb", "name": "results", "type": "ARRAY", "value": None},
            ],
            "ports": [{"id": "d4a097ab-e22d-42f1-b6bc-2ed96856377a", "name": "default", "type": "DEFAULT"}],
            "attributes": [
                {
                    "id": "6cd5395c-6e46-4bc9-b98c-8f8924554555",
                    "name": "ml_model",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "gpt-4o"}},
                },
                {
                    "id": "25f935f3-363f-4ead-a5a0-db234ca67e1e",
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
                    "id": "ffabe7d2-8ab6-4201-9d41-c4d7be1386e1",
                    "name": "prompt_inputs",
                    "value": {
                        "type": "DICTIONARY_REFERENCE",
                        "entries": [
                            {
                                "id": "0bfa70a2-164f-460c-9e9a-4d62221eadf4",
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
                    "id": "8107682b-2ca0-4967-88f9-284455936575",
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
                                    "forced": None,
                                    "strict": None,
                                }
                            ],
                        },
                    },
                },
                {
                    "id": "2b98319f-f43d-42d9-a8b0-b148d5de0a2c",
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

    final_output_node = workflow_raw_data["nodes"][2]
    assert not DeepDiff(
        {
            "id": "42318326-3ae8-417f-9609-f6d8ae47eafb",
            "type": "TERMINAL",
            "data": {
                "label": "Final Output",
                "name": "results",
                "target_handle_id": "46c99277-2b4b-477d-851c-ea497aef6b16",
                "output_id": "15a0ab89-8ed4-43b9-afa2-3c0b29d4dc3e",
                "output_type": "JSON",
                "node_input_id": "d7c89dce-765b-494d-a256-aba4bcf87b42",
            },
            "inputs": [
                {
                    "id": "d7c89dce-765b-494d-a256-aba4bcf87b42",
                    "key": "node_input",
                    "value": {
                        "rules": [
                            {
                                "type": "NODE_OUTPUT",
                                "data": {
                                    "node_id": "8450dd06-975a-41a4-a564-808ee8808fe6",
                                    "output_id": "628df199-a049-40b9-a29b-a378edd759bb",
                                },
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "display_data": {"position": {"x": 400.0, "y": -50.0}},
            "base": {
                "name": "FinalOutputNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
            },
            "definition": None,
        },
        final_output_node,
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "924f693f-3f4c-466a-8cde-648ba3baf9fd",
                "source_node_id": "382842a3-0490-4dee-b87b-eef86766f07c",
                "source_handle_id": "8294baa6-8bf4-4b54-a56b-407b64851b77",
                "target_node_id": "8450dd06-975a-41a4-a564-808ee8808fe6",
                "target_handle_id": "c2dccecb-8a41-40a8-95af-325d3ab8bfe5",
                "type": "DEFAULT",
            },
            {
                "id": "05ca58fb-e02d-48d4-9207-2dad0833a25b",
                "source_node_id": "8450dd06-975a-41a4-a564-808ee8808fe6",
                "source_handle_id": "d4a097ab-e22d-42f1-b6bc-2ed96856377a",
                "target_node_id": "42318326-3ae8-417f-9609-f6d8ae47eafb",
                "target_handle_id": "46c99277-2b4b-477d-851c-ea497aef6b16",
                "type": "DEFAULT",
            },
        ],
        serialized_edges,
        ignore_order=True,
    )

    # AND the display data should be what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {
        "viewport": {
            "x": 0.0,
            "y": 0.0,
            "zoom": 1.0,
        }
    }

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
        "node_id": "cb1186e0-8ff1-4145-823e-96b3fc05a39a",
        "node_output_id": "470fadb9-b8b5-477e-a502-5209d398bcf9",
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
                    "id": "24a203be-3cba-4b20-bc84-9993a476c120",
                    "key": "block_type",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "CHAT_MESSAGE"}},
                },
                {
                    "id": "c06269e6-f74c-4860-8fa5-22dcbdc89399",
                    "key": "state",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                },
                {
                    "id": "dd9c0d43-b931-4dc8-8b3a-a7507ddff0c1",
                    "key": "cache_config",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                },
                {
                    "id": "bef22f2b-0b6e-4910-88cc-6df736d2e20e",
                    "key": "chat_role",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "SYSTEM"}},
                },
                {
                    "id": "c0beec30-f85e-4a78-a3fb-baee54a692f8",
                    "key": "chat_source",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                },
                {
                    "id": "f601f4f2-62fe-4697-9fe0-99ca8aa64500",
                    "key": "chat_message_unterminated",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                },
                {
                    "id": "ad550008-64e3-44a3-a32a-84ec226db31c",
                    "key": "blocks",
                    "value": {
                        "items": [
                            {
                                "lhs": {
                                    "node_id": "9fe5d3a3-7d26-4692-aa2d-e67c673b0c2b",
                                    "node_output_id": "92f9a1b7-d33b-4f00-b4c2-e6f58150e166",
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
        "state_variable_id": "6012a4f7-a8ff-464d-bd62-7c41fde06fa4",
    }
    assert chat_history_entry["value"]["rhs"] == {
        "type": "CONSTANT_VALUE",
        "value": {
            "type": "JSON",
            "value": [],
        },
    }
