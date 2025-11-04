import pytest

from deepdiff import DeepDiff

from vellum.workflows.expressions.begins_with import BeginsWithExpression
from vellum.workflows.expressions.between import BetweenExpression
from vellum.workflows.expressions.contains import ContainsExpression
from vellum.workflows.expressions.does_not_begin_with import DoesNotBeginWithExpression
from vellum.workflows.expressions.does_not_contain import DoesNotContainExpression
from vellum.workflows.expressions.does_not_end_with import DoesNotEndWithExpression
from vellum.workflows.expressions.does_not_equal import DoesNotEqualExpression
from vellum.workflows.expressions.ends_with import EndsWithExpression
from vellum.workflows.expressions.equals import EqualsExpression
from vellum.workflows.expressions.greater_than import GreaterThanExpression
from vellum.workflows.expressions.greater_than_or_equal_to import GreaterThanOrEqualToExpression
from vellum.workflows.expressions.in_ import InExpression
from vellum.workflows.expressions.is_not_null import IsNotNullExpression
from vellum.workflows.expressions.is_null import IsNullExpression
from vellum.workflows.expressions.less_than import LessThanExpression
from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression
from vellum.workflows.expressions.not_between import NotBetweenExpression
from vellum.workflows.expressions.not_in import NotInExpression
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_conditional_node.workflow import CategoryWorkflow
from tests.workflows.basic_conditional_node.workflow_with_only_one_conditional_node import create_simple_workflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a ConditionalNode
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=CategoryWorkflow)
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
                "id": "eece050a-432e-4a2c-8c87-9480397e4cbf",
                "key": "category",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 5
    assert not DeepDiff(
        [
            {
                "id": "c05f7d96-59a0-4d58-93d7-d451afd3f630",
                "key": "question",
                "type": "STRING",
            },
            {
                "id": "93f2cb75-6fa2-4e46-9488-c0bcd29153c0",
                "key": "compliment",
                "type": "STRING",
            },
            {
                "id": "f936ae31-ba15-4864-8961-86231022a4d7",
                "key": "complaint",
                "type": "STRING",
            },
            {
                "id": "cdbe2adf-9951-409a-b9a8-b8b349037f4f",
                "key": "statement",
                "type": "STRING",
            },
            {
                "id": "62ad462f-f819-4940-99ab-b3f145507f57",
                "key": "fallthrough",
                "type": "STRING",
            },
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["edges"]) == 11
    assert len(workflow_raw_data["nodes"]) == 12

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "089b3201-537a-4ed7-8d15-2524a00e8534",
        "type": "ENTRYPOINT",
        "base": None,
        "definition": None,
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "c2f0871d-0d9d-417f-8b0e-c813ccf880ac",
        },
        "display_data": {
            "position": {"x": 0.0, "y": -50.0},
        },
    }

    conditional_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "23e4bbef-6127-49b1-8011-27b2508a60d8",
            "type": "CONDITIONAL",
            "inputs": [
                {
                    "id": "6927a094-4eda-4e97-a759-233bc4a84c28",
                    "key": "7034b205-0b48-494a-a29f-0d22772e9dbf.field",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "8ec07ec7-076e-4c6c-ae25-3e234c96ccf5",
                    "key": "7034b205-0b48-494a-a29f-0d22772e9dbf.value",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "question"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "df55c731-dcae-49cc-8832-182a542a3635",
                    "key": "c0a5254d-5e41-420c-807d-93503e394d8a.field",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "f8b3ab58-1429-4d41-8a8d-6189cecf61f8",
                    "key": "c0a5254d-5e41-420c-807d-93503e394d8a.value",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "complaint"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "04b98bde-48bd-4f4b-bf12-b556fcc409ad",
                    "key": "d2c25be7-a0cc-45d9-9341-fd97aa2a9fbe.field",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "047cd3a4-9dee-42ab-ad77-67400e49aa9c",
                    "key": "d2c25be7-a0cc-45d9-9341-fd97aa2a9fbe.value",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "compliment"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "e92b1631-58b5-4eb8-a446-e316a06d845a",
                    "key": "6163c855-9ff3-42cf-b284-88a9285e393d.field",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "4a1bdf26-afc7-4885-80af-f76f2a55a205",
                    "key": "6163c855-9ff3-42cf-b284-88a9285e393d.value",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "statement"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "0945b52e-f721-488c-ad96-c13a76c6b36b",
                    "key": "aada758f-5662-4597-9fcc-a7b97e7e49c4.field",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "f7905ea6-7c12-4ac8-818b-c1561a0c3b6c",
                    "key": "aada758f-5662-4597-9fcc-a7b97e7e49c4.value",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "statement"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "6a057146-e73b-4848-b62f-4bbf5e07880b",
                    "key": "c56528ee-12e9-4eab-a029-ef4f40633fb5.field",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "2537d049-b71c-48f8-a934-9bd28df6bce2",
                    "key": "c56528ee-12e9-4eab-a029-ef4f40633fb5.value",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "statement"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
            ],
            "data": {
                "label": "Category Conditional Node",
                "target_handle_id": "31e71b98-f5fe-4181-82d1-d16a820a15ca",
                "conditions": [
                    {
                        "id": "09919c37-daa9-4861-8e63-1529d5c279ef",
                        "type": "IF",
                        "source_handle_id": "67fe1e1b-97c3-441c-aedb-887df848bc8a",
                        "data": {
                            "id": "50e4bab9-c70f-441f-8956-61902b4c2ff6",
                            "rules": [
                                {
                                    "id": "7034b205-0b48-494a-a29f-0d22772e9dbf",
                                    "rules": None,
                                    "combinator": None,
                                    "negated": False,
                                    "field_node_input_id": "6927a094-4eda-4e97-a759-233bc4a84c28",
                                    "operator": "=",
                                    "value_node_input_id": "8ec07ec7-076e-4c6c-ae25-3e234c96ccf5",
                                }
                            ],
                            "combinator": "AND",
                            "negated": False,
                            "field_node_input_id": None,
                            "operator": None,
                            "value_node_input_id": None,
                        },
                    },
                    {
                        "id": "ea750051-0409-49ac-8a77-2369bf805776",
                        "type": "ELIF",
                        "source_handle_id": "0d084c4f-1c0b-4029-ab53-a69cc486be1b",
                        "data": {
                            "id": "d5997bf7-7df6-407c-9d9e-2d7264f0cbde",
                            "rules": [
                                {
                                    "id": "c0a5254d-5e41-420c-807d-93503e394d8a",
                                    "rules": None,
                                    "combinator": None,
                                    "negated": False,
                                    "field_node_input_id": "df55c731-dcae-49cc-8832-182a542a3635",
                                    "operator": "=",
                                    "value_node_input_id": "f8b3ab58-1429-4d41-8a8d-6189cecf61f8",
                                }
                            ],
                            "combinator": "AND",
                            "negated": False,
                            "field_node_input_id": None,
                            "operator": None,
                            "value_node_input_id": None,
                        },
                    },
                    {
                        "id": "43025985-122d-4c1a-83a4-d7f7646821e0",
                        "type": "ELIF",
                        "source_handle_id": "d49e16ad-9493-4f58-b881-936b93ca2f7f",
                        "data": {
                            "id": "8208327f-879d-41fc-a976-39be6b0c3904",
                            "rules": [
                                {
                                    "id": "d2c25be7-a0cc-45d9-9341-fd97aa2a9fbe",
                                    "rules": None,
                                    "combinator": None,
                                    "negated": False,
                                    "field_node_input_id": "04b98bde-48bd-4f4b-bf12-b556fcc409ad",
                                    "operator": "=",
                                    "value_node_input_id": "047cd3a4-9dee-42ab-ad77-67400e49aa9c",
                                }
                            ],
                            "combinator": "AND",
                            "negated": False,
                            "field_node_input_id": None,
                            "operator": None,
                            "value_node_input_id": None,
                        },
                    },
                    {
                        "id": "fa5810d6-c98a-431c-9b49-7afd5f135927",
                        "type": "ELIF",
                        "source_handle_id": "0b0024bf-b10a-45fd-995c-e226bbe78fcb",
                        "data": {
                            "id": "b3597697-90d1-491c-b136-ca267e1dae2f",
                            "rules": [
                                {
                                    "id": "6163c855-9ff3-42cf-b284-88a9285e393d",
                                    "rules": None,
                                    "combinator": None,
                                    "negated": False,
                                    "field_node_input_id": "e92b1631-58b5-4eb8-a446-e316a06d845a",
                                    "operator": "=",
                                    "value_node_input_id": "4a1bdf26-afc7-4885-80af-f76f2a55a205",
                                },
                                {
                                    "id": "488ca06f-1ae6-46ee-8f83-919bc90559e8",
                                    "rules": [
                                        {
                                            "id": "aada758f-5662-4597-9fcc-a7b97e7e49c4",
                                            "rules": None,
                                            "combinator": None,
                                            "negated": False,
                                            "field_node_input_id": "0945b52e-f721-488c-ad96-c13a76c6b36b",
                                            "operator": "=",
                                            "value_node_input_id": "f7905ea6-7c12-4ac8-818b-c1561a0c3b6c",
                                        },
                                        {
                                            "id": "c56528ee-12e9-4eab-a029-ef4f40633fb5",
                                            "rules": None,
                                            "combinator": None,
                                            "negated": False,
                                            "field_node_input_id": "6a057146-e73b-4848-b62f-4bbf5e07880b",
                                            "operator": "=",
                                            "value_node_input_id": "2537d049-b71c-48f8-a934-9bd28df6bce2",
                                        },
                                    ],
                                    "combinator": "AND",
                                    "negated": False,
                                    "field_node_input_id": None,
                                    "operator": None,
                                    "value_node_input_id": None,
                                },
                            ],
                            "combinator": "AND",
                            "negated": False,
                            "field_node_input_id": None,
                            "operator": None,
                            "value_node_input_id": None,
                        },
                    },
                    {
                        "id": "4773ebec-866e-47f8-a57f-f9b04b704670",
                        "type": "ELSE",
                        "source_handle_id": "92cbdaf9-496c-48ba-9eec-7d5a3b0d1593",
                        "data": None,
                    },
                ],
                "version": "2",
            },
            "display_data": {"position": {"x": 200.0, "y": -50.0}},
            "base": {
                "name": "ConditionalNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "conditional_node", "node"],
            },
            "definition": {
                "name": "CategoryConditionalNode",
                "module": ["tests", "workflows", "basic_conditional_node", "workflow"],
            },
            "trigger": {
                "id": "31e71b98-f5fe-4181-82d1-d16a820a15ca",
                "merge_behavior": "AWAIT_ANY",
            },
            "ports": [
                {
                    "id": "67fe1e1b-97c3-441c-aedb-887df848bc8a",
                    "name": "category_question",
                    "type": "IF",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "WORKFLOW_INPUT", "input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                        "operator": "=",
                        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "question"}},
                    },
                },
                {
                    "id": "0d084c4f-1c0b-4029-ab53-a69cc486be1b",
                    "name": "category_complaint",
                    "type": "ELIF",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "WORKFLOW_INPUT", "input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                        "operator": "=",
                        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "complaint"}},
                    },
                },
                {
                    "id": "d49e16ad-9493-4f58-b881-936b93ca2f7f",
                    "name": "category_compliment",
                    "type": "ELIF",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "WORKFLOW_INPUT", "input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf"},
                        "operator": "=",
                        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "compliment"}},
                    },
                },
                {
                    "id": "0b0024bf-b10a-45fd-995c-e226bbe78fcb",
                    "name": "category_statement",
                    "type": "ELIF",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {
                            "type": "BINARY_EXPRESSION",
                            "lhs": {
                                "type": "WORKFLOW_INPUT",
                                "input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf",
                            },
                            "operator": "=",
                            "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "statement"}},
                        },
                        "operator": "and",
                        "rhs": {
                            "type": "BINARY_EXPRESSION",
                            "lhs": {
                                "type": "BINARY_EXPRESSION",
                                "lhs": {
                                    "type": "WORKFLOW_INPUT",
                                    "input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf",
                                },
                                "operator": "=",
                                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "statement"}},
                            },
                            "operator": "and",
                            "rhs": {
                                "type": "BINARY_EXPRESSION",
                                "lhs": {
                                    "type": "WORKFLOW_INPUT",
                                    "input_variable_id": "eece050a-432e-4a2c-8c87-9480397e4cbf",
                                },
                                "operator": "=",
                                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "statement"}},
                            },
                        },
                    },
                },
                {
                    "id": "92cbdaf9-496c-48ba-9eec-7d5a3b0d1593",
                    "name": "category_fallthrough",
                    "type": "ELSE",
                    "expression": None,
                },
            ],
        },
        conditional_node,
        ignore_order=True,
    )

    passthrough_nodes = [node for node in workflow_raw_data["nodes"] if node["type"] == "GENERIC"]
    assert len(passthrough_nodes) == 5

    assert not DeepDiff(
        [
            {
                "id": "9c22ee47-01da-4e4e-863d-b4a6874bed66",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "statement",
                    "target_handle_id": "f02a8971-e9a4-4716-bfb4-d08f5614b5d8",
                    "output_id": "cdbe2adf-9951-409a-b9a8-b8b349037f4f",
                    "output_type": "STRING",
                    "node_input_id": "2e742a40-cbee-4e19-9269-c62dc4a9204e",
                },
                "inputs": [
                    {
                        "id": "2e742a40-cbee-4e19-9269-c62dc4a9204e",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "ed7caf01-9ae7-47a3-b15a-16697abaf486",
                                        "output_id": "74ea6af1-8934-4e3c-b68d-b93092b4be73",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 600.0, "y": -50.0}},
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
            {
                "id": "47f0931c-41f6-4b84-bf39-0c486941f599",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "compliment",
                    "target_handle_id": "a4d57adc-58c1-40c6-810b-ee5fd923bfc5",
                    "output_id": "93f2cb75-6fa2-4e46-9488-c0bcd29153c0",
                    "output_type": "STRING",
                    "node_input_id": "9ba792e6-55e3-4a14-8768-e8ef6955c934",
                },
                "inputs": [
                    {
                        "id": "9ba792e6-55e3-4a14-8768-e8ef6955c934",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "8df781b1-ff28-48a5-98a2-d7d796b932b0",
                                        "output_id": "61c357a1-41d8-4adf-bfe1-ce615c4d7d23",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 600.0, "y": -550.0}},
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
            {
                "id": "e3d29229-f746-4125-819e-f847acbed307",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "complaint",
                    "target_handle_id": "c5dd9bf5-9e18-4dbc-8c20-2c0baf969ebe",
                    "output_id": "f936ae31-ba15-4864-8961-86231022a4d7",
                    "output_type": "STRING",
                    "node_input_id": "47f426a4-8770-4f30-a285-5d21849063a5",
                },
                "inputs": [
                    {
                        "id": "47f426a4-8770-4f30-a285-5d21849063a5",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "68c02b7c-5077-4087-803d-841474a8081f",
                                        "output_id": "0ec68ffe-cbb7-4dbb-aaff-f6025bd62efa",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 600.0, "y": 200.0}},
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
            {
                "id": "6efa7b45-0580-406d-85aa-439117ba8021",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "fallthrough",
                    "target_handle_id": "2283cd2c-b077-4b5d-a96f-aa2cd6023eda",
                    "output_id": "62ad462f-f819-4940-99ab-b3f145507f57",
                    "output_type": "STRING",
                    "node_input_id": "d2d3e7cc-f6d6-4ac1-ad19-e6f52a75b38f",
                },
                "inputs": [
                    {
                        "id": "d2d3e7cc-f6d6-4ac1-ad19-e6f52a75b38f",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "148c61bd-e8b0-4d4b-8734-b043a72b90ed",
                                        "output_id": "fafa0bde-8508-43d5-a9c8-db5d49f307f6",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 600.0, "y": -300.0}},
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
            {
                "id": "fa11b84b-1d76-4adc-ab28-cbbaa933c267",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "question",
                    "target_handle_id": "e1a6da28-02c5-40d7-8ac5-9fb07e2e3e1d",
                    "output_id": "c05f7d96-59a0-4d58-93d7-d451afd3f630",
                    "output_type": "STRING",
                    "node_input_id": "a13377c4-ae1c-4be4-b695-f9da590486ef",
                },
                "inputs": [
                    {
                        "id": "a13377c4-ae1c-4be4-b695-f9da590486ef",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "0d959311-c836-4641-a867-58f63df9dfea",
                                        "output_id": "db9f7ff3-77e2-4b0a-9c39-bb4bb50e3ad5",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 600.0, "y": 450.0}},
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
        ],
        workflow_raw_data["nodes"][7:12],
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "8bc5a416-7e46-473e-b16a-ad5a54eb0d84",
                "source_node_id": "089b3201-537a-4ed7-8d15-2524a00e8534",
                "source_handle_id": "c2f0871d-0d9d-417f-8b0e-c813ccf880ac",
                "target_node_id": "23e4bbef-6127-49b1-8011-27b2508a60d8",
                "target_handle_id": "31e71b98-f5fe-4181-82d1-d16a820a15ca",
                "type": "DEFAULT",
            },
            {
                "id": "b5ecb4de-9a1b-473f-8a29-102b5d4d58d0",
                "source_node_id": "23e4bbef-6127-49b1-8011-27b2508a60d8",
                "source_handle_id": "67fe1e1b-97c3-441c-aedb-887df848bc8a",
                "target_node_id": "0d959311-c836-4641-a867-58f63df9dfea",
                "target_handle_id": "7beba198-c452-4749-a38a-ea9420d84e14",
                "type": "DEFAULT",
            },
            {
                "id": "88a40d2b-ec50-44de-b850-ca98199b87e2",
                "source_node_id": "23e4bbef-6127-49b1-8011-27b2508a60d8",
                "source_handle_id": "0d084c4f-1c0b-4029-ab53-a69cc486be1b",
                "target_node_id": "68c02b7c-5077-4087-803d-841474a8081f",
                "target_handle_id": "1dc4eebe-b6db-4229-96e5-115ff8cedb76",
                "type": "DEFAULT",
            },
            {
                "id": "7be94c9a-3eaa-4b0d-bdb7-481e4ff89c30",
                "source_node_id": "23e4bbef-6127-49b1-8011-27b2508a60d8",
                "source_handle_id": "d49e16ad-9493-4f58-b881-936b93ca2f7f",
                "target_node_id": "8df781b1-ff28-48a5-98a2-d7d796b932b0",
                "target_handle_id": "b73c39be-cbfe-4225-86e6-e6e4c161881e",
                "type": "DEFAULT",
            },
            {
                "id": "c739fa75-ce90-4972-8eb6-22fcbc86d97f",
                "source_node_id": "23e4bbef-6127-49b1-8011-27b2508a60d8",
                "source_handle_id": "0b0024bf-b10a-45fd-995c-e226bbe78fcb",
                "target_node_id": "ed7caf01-9ae7-47a3-b15a-16697abaf486",
                "target_handle_id": "76fe7aec-5cd4-4c1a-b386-cfe09ebe66e4",
                "type": "DEFAULT",
            },
            {
                "id": "bb169e6f-cfb2-48ec-b40c-40a863bfaa48",
                "source_node_id": "23e4bbef-6127-49b1-8011-27b2508a60d8",
                "source_handle_id": "92cbdaf9-496c-48ba-9eec-7d5a3b0d1593",
                "target_node_id": "148c61bd-e8b0-4d4b-8734-b043a72b90ed",
                "target_handle_id": "c88839af-3a79-4310-abbd-e1553d981dce",
                "type": "DEFAULT",
            },
            {
                "id": "8a554637-e382-4a66-9b77-4eadce45a25a",
                "source_node_id": "ed7caf01-9ae7-47a3-b15a-16697abaf486",
                "source_handle_id": "cde43aef-f607-4b5d-87f6-9238dd4a3a2b",
                "target_node_id": "9c22ee47-01da-4e4e-863d-b4a6874bed66",
                "target_handle_id": "f02a8971-e9a4-4716-bfb4-d08f5614b5d8",
                "type": "DEFAULT",
            },
            {
                "id": "af083f7d-226c-4341-bb6f-756f00846b42",
                "source_node_id": "68c02b7c-5077-4087-803d-841474a8081f",
                "source_handle_id": "ef032cf7-c8df-4a98-827c-386dd8a5a346",
                "target_node_id": "e3d29229-f746-4125-819e-f847acbed307",
                "target_handle_id": "c5dd9bf5-9e18-4dbc-8c20-2c0baf969ebe",
                "type": "DEFAULT",
            },
            {
                "id": "47758209-70cb-4f12-b71f-dc28df0f6d0b",
                "source_node_id": "0d959311-c836-4641-a867-58f63df9dfea",
                "source_handle_id": "69a2121d-fc21-47a1-af49-6200aad836de",
                "target_node_id": "fa11b84b-1d76-4adc-ab28-cbbaa933c267",
                "target_handle_id": "e1a6da28-02c5-40d7-8ac5-9fb07e2e3e1d",
                "type": "DEFAULT",
            },
            {
                "id": "f08a49f8-8bfd-4c05-8f28-dfa536654af8",
                "source_node_id": "8df781b1-ff28-48a5-98a2-d7d796b932b0",
                "source_handle_id": "aeb6805d-2c9f-4d52-a690-341ea0e869b3",
                "target_node_id": "47f0931c-41f6-4b84-bf39-0c486941f599",
                "target_handle_id": "a4d57adc-58c1-40c6-810b-ee5fd923bfc5",
                "type": "DEFAULT",
            },
            {
                "id": "c45e03b4-dba6-4620-bc02-3847ad90086b",
                "source_node_id": "148c61bd-e8b0-4d4b-8734-b043a72b90ed",
                "source_handle_id": "26f50353-85ae-462f-b82d-9fd736900bd6",
                "target_node_id": "6efa7b45-0580-406d-85aa-439117ba8021",
                "target_handle_id": "2283cd2c-b077-4b5d-a96f-aa2cd6023eda",
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
        "name": "CategoryWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_conditional_node",
            "workflow",
        ],
    }


def descriptors_with_lhs_and_rhs():
    return [
        (EqualsExpression(lhs="123", rhs="123"), "="),
        (DoesNotEqualExpression(lhs="123", rhs="123"), "!="),
        (LessThanExpression(lhs="123", rhs="123"), "<"),
        (GreaterThanExpression(lhs="123", rhs="123"), ">"),
        (LessThanOrEqualToExpression(lhs="123", rhs="123"), "<="),
        (GreaterThanOrEqualToExpression(lhs="123", rhs="123"), ">="),
        (ContainsExpression(lhs="123", rhs="123"), "contains"),
        (BeginsWithExpression(lhs="123", rhs="123"), "beginsWith"),
        (EndsWithExpression(lhs="123", rhs="123"), "endsWith"),
        (DoesNotContainExpression(lhs="123", rhs="123"), "doesNotContain"),
        (DoesNotBeginWithExpression(lhs="123", rhs="123"), "doesNotBeginWith"),
        (DoesNotEndWithExpression(lhs="123", rhs="123"), "doesNotEndWith"),
        (InExpression(lhs="123", rhs="123"), "in"),
        (NotInExpression(lhs="123", rhs="123"), "notIn"),
    ]


def descriptors_with_expression():
    return [
        (IsNullExpression(expression="123"), "null"),
        (IsNotNullExpression(expression="123"), "notNull"),
    ]


def descriptors_with_value_and_start_and_end():
    return [
        (BetweenExpression(value="123", start="123", end="123"), "between"),
        (NotBetweenExpression(value="123", start="123", end="123"), "notBetween"),
    ]


@pytest.mark.parametrize("descriptor, operator", descriptors_with_lhs_and_rhs())
def test_conditional_node_serialize_all_operators_with_lhs_and_rhs(descriptor, operator):
    # GIVEN a simple workflow with one conditional node
    workflow_cls = create_simple_workflow(descriptor)

    workflow_display = get_workflow_display(workflow_class=workflow_cls)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND the conditional node should be what we expect
    conditional_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "9d1b29dc-b795-415f-8a56-bea2c77bbf1a",
            "type": "CONDITIONAL",
            "inputs": [
                {
                    "id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                    "key": "f497b2bf-7d35-43af-b162-ced2d8abd46f.field",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "123"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "c9d3791a-da39-42b4-83cd-2205cd2beece",
                    "key": "f497b2bf-7d35-43af-b162-ced2d8abd46f.value",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "123"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
            ],
            "data": {
                "label": "Simple Conditional Node",
                "target_handle_id": "82348aaa-655f-47ef-8a7c-96a618b0aab0",
                "conditions": [
                    {
                        "id": "4d325440-5c08-4669-9ac2-df56dc97205c",
                        "type": "IF",
                        "source_handle_id": "90f7bb16-87b5-48dd-a14a-5dc12e8347d6",
                        "data": {
                            "id": "650e7105-3e76-43ca-858f-b290970b438b",
                            "rules": [
                                {
                                    "id": "f497b2bf-7d35-43af-b162-ced2d8abd46f",
                                    "rules": None,
                                    "combinator": None,
                                    "negated": False,
                                    "field_node_input_id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                                    "operator": f"{operator}",
                                    "value_node_input_id": "c9d3791a-da39-42b4-83cd-2205cd2beece",
                                }
                            ],
                            "combinator": "AND",
                            "negated": False,
                            "field_node_input_id": None,
                            "operator": None,
                            "value_node_input_id": None,
                        },
                    },
                    {
                        "id": "5d164388-d76d-4bf1-9a88-a9fb8e797cbe",
                        "type": "ELSE",
                        "source_handle_id": "a66da8a4-7148-4554-a63c-38d20643cbb7",
                        "data": None,
                    },
                ],
                "version": "2",
            },
            "display_data": {"position": {"x": 200.0, "y": -50.0}},
            "base": {
                "name": "ConditionalNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "conditional_node", "node"],
            },
            "definition": {
                "name": "SimpleConditionalNode",
                "module": ["tests", "workflows", "basic_conditional_node", "workflow_with_only_one_conditional_node"],
            },
            "trigger": {
                "id": "82348aaa-655f-47ef-8a7c-96a618b0aab0",
                "merge_behavior": "AWAIT_ANY",
            },
            "ports": [
                {
                    "id": "90f7bb16-87b5-48dd-a14a-5dc12e8347d6",
                    "name": "text_str",
                    "type": "IF",
                    "expression": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "123"}},
                        "operator": f"{operator}",
                        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "123"}},
                    },
                },
                {
                    "id": "a66da8a4-7148-4554-a63c-38d20643cbb7",
                    "name": "text_fallthrough",
                    "type": "ELSE",
                    "expression": None,
                },
            ],
        },
        conditional_node,
        ignore_order=True,
    )


@pytest.mark.parametrize("descriptor, operator", descriptors_with_expression())
def test_conditional_node_serialize_all_operators_with_expression(descriptor, operator):
    # GIVEN a simple workflow with one conditional node
    workflow_cls = create_simple_workflow(descriptor)

    workflow_display = get_workflow_display(workflow_class=workflow_cls)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND the conditional node should be what we expect
    conditional_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "9d1b29dc-b795-415f-8a56-bea2c77bbf1a",
            "type": "CONDITIONAL",
            "inputs": [
                {
                    "id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                    "key": "f497b2bf-7d35-43af-b162-ced2d8abd46f.field",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "123"},
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "data": {
                "label": "Simple Conditional Node",
                "target_handle_id": "82348aaa-655f-47ef-8a7c-96a618b0aab0",
                "conditions": [
                    {
                        "id": "4d325440-5c08-4669-9ac2-df56dc97205c",
                        "type": "IF",
                        "source_handle_id": "90f7bb16-87b5-48dd-a14a-5dc12e8347d6",
                        "data": {
                            "id": "650e7105-3e76-43ca-858f-b290970b438b",
                            "rules": [
                                {
                                    "id": "f497b2bf-7d35-43af-b162-ced2d8abd46f",
                                    "rules": None,
                                    "combinator": None,
                                    "negated": False,
                                    "field_node_input_id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                                    "operator": f"{operator}",
                                    "value_node_input_id": "c9d3791a-da39-42b4-83cd-2205cd2beece",
                                }
                            ],
                            "combinator": "AND",
                            "negated": False,
                            "field_node_input_id": None,
                            "operator": None,
                            "value_node_input_id": None,
                        },
                    },
                    {
                        "id": "5d164388-d76d-4bf1-9a88-a9fb8e797cbe",
                        "type": "ELSE",
                        "source_handle_id": "a66da8a4-7148-4554-a63c-38d20643cbb7",
                        "data": None,
                    },
                ],
                "version": "2",
            },
            "display_data": {"position": {"x": 200.0, "y": -50.0}},
            "base": {
                "name": "ConditionalNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "conditional_node", "node"],
            },
            "definition": {
                "name": "SimpleConditionalNode",
                "module": ["tests", "workflows", "basic_conditional_node", "workflow_with_only_one_conditional_node"],
            },
            "trigger": {
                "id": "82348aaa-655f-47ef-8a7c-96a618b0aab0",
                "merge_behavior": "AWAIT_ANY",
            },
            "ports": [
                {
                    "id": "90f7bb16-87b5-48dd-a14a-5dc12e8347d6",
                    "name": "text_str",
                    "type": "IF",
                    "expression": {
                        "type": "UNARY_EXPRESSION",
                        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "123"}},
                        "operator": f"{operator}",
                    },
                },
                {
                    "id": "a66da8a4-7148-4554-a63c-38d20643cbb7",
                    "name": "text_fallthrough",
                    "type": "ELSE",
                    "expression": None,
                },
            ],
        },
        conditional_node,
        ignore_order=True,
    )


@pytest.mark.parametrize("descriptor, operator", descriptors_with_value_and_start_and_end())
def test_conditional_node_serialize_all_operators_with_value_and_start_and_end(descriptor, operator):
    # GIVEN a simple workflow with one conditional node
    workflow_cls = create_simple_workflow(descriptor)

    workflow_display = get_workflow_display(workflow_class=workflow_cls)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND the conditional node should be what we expect
    conditional_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "9d1b29dc-b795-415f-8a56-bea2c77bbf1a",
            "type": "CONDITIONAL",
            "inputs": [
                {
                    "id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                    "key": "f497b2bf-7d35-43af-b162-ced2d8abd46f.field",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "123"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
                {
                    "id": "c9d3791a-da39-42b4-83cd-2205cd2beece",
                    "key": "f497b2bf-7d35-43af-b162-ced2d8abd46f.value",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "123,123"},
                            }
                        ],
                        "combinator": "OR",
                    },
                },
            ],
            "data": {
                "label": "Simple Conditional Node",
                "target_handle_id": "82348aaa-655f-47ef-8a7c-96a618b0aab0",
                "conditions": [
                    {
                        "id": "4d325440-5c08-4669-9ac2-df56dc97205c",
                        "type": "IF",
                        "source_handle_id": "90f7bb16-87b5-48dd-a14a-5dc12e8347d6",
                        "data": {
                            "id": "650e7105-3e76-43ca-858f-b290970b438b",
                            "rules": [
                                {
                                    "id": "f497b2bf-7d35-43af-b162-ced2d8abd46f",
                                    "rules": None,
                                    "combinator": None,
                                    "negated": False,
                                    "field_node_input_id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                                    "operator": f"{operator}",
                                    "value_node_input_id": "c9d3791a-da39-42b4-83cd-2205cd2beece",
                                }
                            ],
                            "combinator": "AND",
                            "negated": False,
                            "field_node_input_id": None,
                            "operator": None,
                            "value_node_input_id": None,
                        },
                    },
                    {
                        "id": "5d164388-d76d-4bf1-9a88-a9fb8e797cbe",
                        "type": "ELSE",
                        "source_handle_id": "a66da8a4-7148-4554-a63c-38d20643cbb7",
                        "data": None,
                    },
                ],
                "version": "2",
            },
            "display_data": {"position": {"x": 200.0, "y": -50.0}},
            "base": {
                "name": "ConditionalNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "conditional_node", "node"],
            },
            "definition": {
                "name": "SimpleConditionalNode",
                "module": ["tests", "workflows", "basic_conditional_node", "workflow_with_only_one_conditional_node"],
            },
            "trigger": {
                "id": "82348aaa-655f-47ef-8a7c-96a618b0aab0",
                "merge_behavior": "AWAIT_ANY",
            },
            "ports": [
                {
                    "id": "90f7bb16-87b5-48dd-a14a-5dc12e8347d6",
                    "name": "text_str",
                    "type": "IF",
                    "expression": {
                        "type": "TERNARY_EXPRESSION",
                        "base": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "123"}},
                        "operator": f"{operator}",
                        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "123"}},
                        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "123"}},
                    },
                },
                {
                    "id": "a66da8a4-7148-4554-a63c-38d20643cbb7",
                    "name": "text_fallthrough",
                    "type": "ELSE",
                    "expression": None,
                },
            ],
        },
        conditional_node,
        ignore_order=True,
    )
