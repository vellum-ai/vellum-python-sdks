import uuid

from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.mocks import MockNodeExecution
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay


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
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_execution,
        MyWorkflow,
    )

    # THEN we get a list of MockNodeExecution objects
    assert node_output_mocks
    assert len(node_output_mocks) == 1
    assert node_output_mocks[0] == MockNodeExecution(
        when_condition=PromptNode.Execution.count.greater_than_or_equal_to(0.0),
        then_outputs=PromptNode.Outputs(
            text="Hello",
            results=[
                StringVellumValue(value="Hello"),
            ],
        ),
    )


def test_mocks__parse_none_still_runs():
    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow class with that Node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = StartNode.Outputs.foo

    # AND we parsed `None` on `MockNodeExecution`
    node_output_mocks = MockNodeExecution.validate_all(
        None,
        MyWorkflow,
    )

    # WHEN we run the workflow
    workflow = MyWorkflow()
    final_event = workflow.run(node_output_mocks=node_output_mocks)

    # THEN it was successful
    assert final_event.name == "workflow.execution.fulfilled"


def test_mocks__use_id_from_display():
    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow class with that Node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = StartNode.Outputs.foo

    # AND a display class on that Base Node
    node_output_id = uuid.uuid4()

    class StartNodeDisplay(BaseNodeDisplay[StartNode]):
        output_display = {StartNode.Outputs.foo: NodeOutputDisplay(id=node_output_id, name="foo")}

    # AND a mock workflow node execution from the app
    raw_mock_workflow_node_execution = [
        {
            "type": "WORKFLOW_NODE_OUTPUT",
            "node_id": str(StartNode.__id__),
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
                                "node_id": str(StartNode.__id__),
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
                            "output_id": str(node_output_id),
                            "value": {
                                "id": "27006b2a-fa81-430c-a0b2-c66a9351fc68",
                                "type": "CONSTANT_VALUE",
                                "variable_value": {"type": "STRING", "value": "Hello"},
                            },
                        },
                    ],
                }
            ],
        }
    ]

    # WHEN we parsed the raw data on `MockNodeExecution`
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_execution,
        MyWorkflow,
    )

    # THEN we get the expected list of MockNodeExecution objects
    assert node_output_mocks
    assert len(node_output_mocks) == 1
    assert node_output_mocks[0] == MockNodeExecution(
        when_condition=StartNode.Execution.count.greater_than_or_equal_to(0.0),
        then_outputs=StartNode.Outputs(
            foo="Hello",
        ),
    )
