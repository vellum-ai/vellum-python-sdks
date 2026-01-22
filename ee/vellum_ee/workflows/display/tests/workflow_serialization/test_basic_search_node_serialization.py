from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_search_node.workflow import BasicSearchWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow with a search node
    # WHEN we serialize it

    workflow_display = get_workflow_display(workflow_class=BasicSearchWorkflow)

    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1
    assert input_variables == [
        {
            "id": "6e405c6c-36eb-4c06-9d54-ae06cccce585",
            "key": "query",
            "type": "STRING",
            "default": None,
            "required": True,
            "extensions": {"color": None},
            "schema": {"type": "string"},
        }
    ]

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables == [{"id": "27424f7d-9767-4059-bdcf-c2be8b798fd7", "key": "text", "type": "STRING"}]

    # AND its raw data is what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "06671b25-5c6b-4675-8c74-6c396a608728",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "df80b4aa-2ba1-49a2-8375-fb1f78eee31f"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
    }

    search_node = workflow_raw_data["nodes"][1]
    assert search_node == {
        "id": "89c8bee0-8015-4d73-9112-e436ab086567",
        "type": "SEARCH",
        "inputs": [
            {
                "id": "1dbfd1d9-8e8e-47b6-bb65-c578385ef978",
                "key": "query",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "6e405c6c-36eb-4c06-9d54-ae06cccce585"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "8f197069-4729-4db3-811c-9a522685dfba",
                "key": "document_index_id",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "name"}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "dd991fc6-5690-496b-b63e-b1a1219f3682",
                "key": "weights",
                "value": {
                    "rules": [
                        {
                            "type": "CONSTANT_VALUE",
                            "data": {"type": "JSON", "value": {"keywords": 0.45, "semantic_similarity": 0.55}},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "52f6c3ab-cd96-4ca7-bfb1-7554c431b318",
                "key": "limit",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "JSON", "value": None}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "e1822f91-ca9c-46c9-8dcd-cce83fe331ce",
                "key": "separator",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "\n\n#####\n\n"}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "3ee2bc2a-d72a-471a-8dd6-5e5028db8bfe",
                "key": "result_merging_enabled",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "False"}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "5c766934-13f7-4a0f-a751-21e25fd2ca30",
                "key": "external_id_filters",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "JSON", "value": None}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "977d75bc-520f-447b-ad75-8b56c793f951",
                "key": "metadata_filters",
                "value": {
                    "rules": [
                        {
                            "type": "CONSTANT_VALUE",
                            "data": {
                                "type": "JSON",
                                "value": {
                                    "type": "LOGICAL_CONDITION_GROUP",
                                    "combinator": "AND",
                                    "conditions": [
                                        {
                                            "type": "LOGICAL_CONDITION",
                                            "lhs_variable_id": "a6322ca2-8b65-4d26-b3a1-f926dcada0fa",
                                            "operator": "=",
                                            "rhs_variable_id": "c539a2e2-0873-43b0-ae21-81790bb1c4cb",
                                        },
                                        {
                                            "type": "LOGICAL_CONDITION",
                                            "lhs_variable_id": "a89483b6-6850-4105-8c4e-ec0fd197cd43",
                                            "operator": "=",
                                            "rhs_variable_id": "847b8ee0-2c37-4e41-9dea-b4ba3579e2c1",
                                        },
                                    ],
                                    "negated": False,
                                },
                            },
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "a6322ca2-8b65-4d26-b3a1-f926dcada0fa",
                "key": "vellum-query-builder-variable-a6322ca2-8b65-4d26-b3a1-f926dcada0fa",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "67fd852b-789b-4c18-8465-2bbf1696b8eb"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "c539a2e2-0873-43b0-ae21-81790bb1c4cb",
                "key": "vellum-query-builder-variable-c539a2e2-0873-43b0-ae21-81790bb1c4cb",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "58e909b0-9269-454d-b40d-3846fd2c39f2"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "a89483b6-6850-4105-8c4e-ec0fd197cd43",
                "key": "vellum-query-builder-variable-a89483b6-6850-4105-8c4e-ec0fd197cd43",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "7564f9c7-b2cf-4584-b4c7-845a14ac4dfa"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "847b8ee0-2c37-4e41-9dea-b4ba3579e2c1",
                "key": "vellum-query-builder-variable-847b8ee0-2c37-4e41-9dea-b4ba3579e2c1",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "cd081063-ab26-4ec7-99b3-af7e035a16e3"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Simple Search Node",
            "results_output_id": "184c5214-29be-4029-8ece-2991972e0822",
            "text_output_id": "9bab7f1b-3a4b-46bf-8b30-e3016ac38f51",
            "error_output_id": None,
            "source_handle_id": "928c79f2-bc07-43ee-9420-380a3bd36fb8",
            "target_handle_id": "85db938d-9a85-4f08-8bbf-b795db2c40d5",
            "query_node_input_id": "1dbfd1d9-8e8e-47b6-bb65-c578385ef978",
            "document_index_node_input_id": "8f197069-4729-4db3-811c-9a522685dfba",
            "weights_node_input_id": "dd991fc6-5690-496b-b63e-b1a1219f3682",
            "limit_node_input_id": "52f6c3ab-cd96-4ca7-bfb1-7554c431b318",
            "separator_node_input_id": "e1822f91-ca9c-46c9-8dcd-cce83fe331ce",
            "result_merging_enabled_node_input_id": "3ee2bc2a-d72a-471a-8dd6-5e5028db8bfe",
            "external_id_filters_node_input_id": "5c766934-13f7-4a0f-a751-21e25fd2ca30",
            "metadata_filters_node_input_id": "977d75bc-520f-447b-ad75-8b56c793f951",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "name": "SearchNode",
            "module": ["vellum", "workflows", "nodes", "displayable", "search_node", "node"],
        },
        "definition": {
            "name": "SimpleSearchNode",
            "module": ["tests", "workflows", "basic_search_node", "workflow"],
        },
        "trigger": {
            "id": "85db938d-9a85-4f08-8bbf-b795db2c40d5",
            "merge_behavior": "AWAIT_ANY",
        },
        "ports": [{"id": "928c79f2-bc07-43ee-9420-380a3bd36fb8", "name": "default", "type": "DEFAULT"}],
    }

    # AND the display data is what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}}

    # AND the definition is what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicSearchWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_search_node",
            "workflow",
        ],
    }
