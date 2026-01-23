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
                "schema": {"type": "string"},
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

    # AND each node should be serialized correctly

    conditional_node = next(
        n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "ConditionalNode"
    )
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
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
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
    conditional_node = next(
        n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "ConditionalNode"
    )
    assert not DeepDiff(
        {
            "id": "9d1b29dc-b795-415f-8a56-bea2c77bbf1a",
            "type": "CONDITIONAL",
            "inputs": [
                {
                    "id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                    "key": "12944986-8e31-4501-bc74-4eb00f2d7d2a.field",
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
                    "key": "12944986-8e31-4501-bc74-4eb00f2d7d2a.value",
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
                            "id": "08c6312c-bfe3-4254-affd-8650e48c7f47",
                            "rules": [
                                {
                                    "id": "12944986-8e31-4501-bc74-4eb00f2d7d2a",
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
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
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
    conditional_node = next(
        n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "ConditionalNode"
    )
    assert not DeepDiff(
        {
            "id": "9d1b29dc-b795-415f-8a56-bea2c77bbf1a",
            "type": "CONDITIONAL",
            "inputs": [
                {
                    "id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                    "key": "12944986-8e31-4501-bc74-4eb00f2d7d2a.field",
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
                            "id": "08c6312c-bfe3-4254-affd-8650e48c7f47",
                            "rules": [
                                {
                                    "id": "12944986-8e31-4501-bc74-4eb00f2d7d2a",
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
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
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
    conditional_node = next(
        n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "ConditionalNode"
    )
    assert not DeepDiff(
        {
            "id": "9d1b29dc-b795-415f-8a56-bea2c77bbf1a",
            "type": "CONDITIONAL",
            "inputs": [
                {
                    "id": "3afbc787-fe7d-4411-934e-32c6ad101676",
                    "key": "12944986-8e31-4501-bc74-4eb00f2d7d2a.field",
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
                    "key": "12944986-8e31-4501-bc74-4eb00f2d7d2a.value",
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
                            "id": "08c6312c-bfe3-4254-affd-8650e48c7f47",
                            "rules": [
                                {
                                    "id": "12944986-8e31-4501-bc74-4eb00f2d7d2a",
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
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
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
