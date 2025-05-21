from deepdiff import DeepDiff

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
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
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
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
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
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
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
