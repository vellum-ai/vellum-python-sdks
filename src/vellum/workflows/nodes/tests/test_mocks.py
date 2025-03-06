from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.nodes.mocks import MockNodeExecution


def test_mocks__parse_from_app():
    # GIVEN a PromptNode
    class PromptNode(InlinePromptNode):
        pass

    # AND a workflow class with that PromptNode
    class MyWorkflow(BaseWorkflow):
        graph = PromptNode

    # AND a mock workflow node execution from the app
    raw_mock_workflow_node_execution = [
        {
            "type": "WORKFLOW_NODE_OUTPUT",
            "node_id": str(PromptNode.__id__),
            "mock_executions": [
                {
                    "when_condition": {
                        "expression": {
                            "type": "LOGICAL_CONDITION_GROUP",
                            "combinator": "AND",
                            "negated": False,
                            "conditions": [
                                {
                                    "type": "LOGICAL_CONDITION",
                                    "lhs_variable_id": "e60902d5-6892-4916-80c1-f0130af52322",
                                    "operator": ">=",
                                    "rhs_variable_id": "5c1bbb24-c288-49cb-a9b7-0c6f38a86037",
                                }
                            ],
                        },
                        "variables": [
                            {
                                "type": "EXECUTION_COUNTER",
                                "node_id": str(PromptNode.__id__),
                                "id": "e60902d5-6892-4916-80c1-f0130af52322",
                            },
                            {
                                "type": "CONSTANT_VALUE",
                                "variable_value": {"type": "NUMBER", "value": 0},
                                "id": "5c1bbb24-c288-49cb-a9b7-0c6f38a86037",
                            },
                        ],
                    },
                    "then_outputs": [
                        {
                            "output_id": "9e6dc5d3-8ea0-4346-8a2a-7cce5495755b",
                            "value": {
                                "id": "27006b2a-fa81-430c-a0b2-c66a9351fc68",
                                "type": "CONSTANT_VALUE",
                                "variable_value": {"type": "STRING", "value": "Hello"},
                            },
                        },
                        {
                            "output_id": "60305ffd-60b0-42aa-b54e-4fdae0f8c28a",
                            "value": {
                                "id": "4559c778-6e27-4cfe-a460-734ba62a5082",
                                "type": "CONSTANT_VALUE",
                                "variable_value": {"type": "ARRAY", "value": [{"type": "STRING", "value": "Hello"}]},
                            },
                        },
                    ],
                }
            ],
        }
    ]

    # WHEN we parse the mock workflow node execution
    mock_node_execution = MockNodeExecution.validate_all(
        raw_mock_workflow_node_execution,
        MyWorkflow,
    )

    # THEN we get a list of MockNodeExecution objects
    assert len(mock_node_execution) == 1
    assert mock_node_execution[0] == MockNodeExecution(
        when_condition=PromptNode.Execution.count.greater_than_or_equal_to(0.0),
        then_outputs=PromptNode.Outputs(
            text="Hello",
            results=[
                StringVellumValue(value="Hello"),
            ],
        ),
    )
