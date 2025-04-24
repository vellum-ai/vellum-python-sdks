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
        }
    ]

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables == [{"id": "27424f7d-9767-4059-bdcf-c2be8b798fd7", "key": "text", "type": "STRING"}]

    # AND its raw data is what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["nodes"]) == 3
    assert len(workflow_raw_data["edges"]) == 2

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
        "id": "ab3a1413-c7b5-4cb0-a2d4-f5ab7d1d65b4",
        "type": "SEARCH",
        "inputs": [
            {
                "id": "49d21956-6e62-472b-b62a-7ec65faea1fd",
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
                "id": "8cb28a69-088d-410d-bd0d-886d57ce7b64",
                "key": "document_index_id",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "name"}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "983f2b7f-ad86-45cf-b04b-08724af27236",
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
                "id": "8072ec05-5fe4-47db-bc48-4c20ce49e123",
                "key": "limit",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "JSON", "value": None}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "051c5d2e-4667-4ae2-9202-1076b21adf7b",
                "key": "separator",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "\n\n#####\n\n"}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "8aac5dac-209e-48f3-97e1-0a39e4cd98d5",
                "key": "result_merging_enabled",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "False"}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "036dee8f-194a-4b92-9739-69c98a4aa1b9",
                "key": "external_id_filters",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "JSON", "value": None}}],
                    "combinator": "OR",
                },
            },
            {
                "id": "855d3f57-e633-467e-a348-a394360247df",
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
                            "data": {"input_variable_id": "8ffffeb2-79b3-4105-acc7-78b0267da955"},
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
                            "data": {"input_variable_id": "8ffffeb2-79b3-4105-acc7-78b0267da955"},
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
                            "data": {"input_variable_id": "f5eee974-b0c3-4775-bc8a-679a9e99d7ba"},
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
                            "data": {"input_variable_id": "f5eee974-b0c3-4775-bc8a-679a9e99d7ba"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Simple Search Node",
            "results_output_id": "e27fa934-589a-48f7-92a9-dcc90710ec7b",
            "text_output_id": "3f3bd066-ce73-46ee-84f1-d8ece69ecd8c",
            "error_output_id": None,
            "source_handle_id": "00ae06b3-f8d9-4ae6-9fbf-e4ff4d520e9b",
            "target_handle_id": "6d50305f-588b-469f-a042-b0767d3f99b1",
            "query_node_input_id": "49d21956-6e62-472b-b62a-7ec65faea1fd",
            "document_index_node_input_id": "8cb28a69-088d-410d-bd0d-886d57ce7b64",
            "weights_node_input_id": "983f2b7f-ad86-45cf-b04b-08724af27236",
            "limit_node_input_id": "8072ec05-5fe4-47db-bc48-4c20ce49e123",
            "separator_node_input_id": "051c5d2e-4667-4ae2-9202-1076b21adf7b",
            "result_merging_enabled_node_input_id": "8aac5dac-209e-48f3-97e1-0a39e4cd98d5",
            "external_id_filters_node_input_id": "036dee8f-194a-4b92-9739-69c98a4aa1b9",
            "metadata_filters_node_input_id": "855d3f57-e633-467e-a348-a394360247df",
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
        "ports": [{"id": "00ae06b3-f8d9-4ae6-9fbf-e4ff4d520e9b", "name": "default", "type": "DEFAULT"}],
    }

    final_output_node = workflow_raw_data["nodes"][2]
    assert final_output_node == {
        "id": "4e466510-6756-403f-a182-56e5a2b85d94",
        "type": "TERMINAL",
        "data": {
            "label": "Final Output",
            "name": "text",
            "target_handle_id": "cd8c736f-1b77-493d-b857-d8feb5c03b15",
            "output_id": "27424f7d-9767-4059-bdcf-c2be8b798fd7",
            "output_type": "STRING",
            "node_input_id": "39c7f674-a794-4525-8a04-f22a40ed0914",
        },
        "inputs": [
            {
                "id": "39c7f674-a794-4525-8a04-f22a40ed0914",
                "key": "node_input",
                "value": {
                    "rules": [
                        {
                            "type": "NODE_OUTPUT",
                            "data": {
                                "node_id": "ab3a1413-c7b5-4cb0-a2d4-f5ab7d1d65b4",
                                "output_id": "3f3bd066-ce73-46ee-84f1-d8ece69ecd8c",
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
    }

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert serialized_edges == [
        {
            "id": "06533904-4897-4a7a-aa8d-50419b3d33ae",
            "source_node_id": "06671b25-5c6b-4675-8c74-6c396a608728",
            "source_handle_id": "df80b4aa-2ba1-49a2-8375-fb1f78eee31f",
            "target_node_id": "ab3a1413-c7b5-4cb0-a2d4-f5ab7d1d65b4",
            "target_handle_id": "6d50305f-588b-469f-a042-b0767d3f99b1",
            "type": "DEFAULT",
        },
        {
            "id": "cb918deb-f546-47b5-8b6b-db0d22a29fd1",
            "source_node_id": "ab3a1413-c7b5-4cb0-a2d4-f5ab7d1d65b4",
            "source_handle_id": "00ae06b3-f8d9-4ae6-9fbf-e4ff4d520e9b",
            "target_node_id": "4e466510-6756-403f-a182-56e5a2b85d94",
            "target_handle_id": "cd8c736f-1b77-493d-b857-d8feb5c03b15",
            "type": "DEFAULT",
        },
    ]

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
