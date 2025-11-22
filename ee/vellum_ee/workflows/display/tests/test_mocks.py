from vellum.workflows import BaseInputs, BaseNode, BaseState, BaseWorkflow, MockNodeExecution
from vellum_ee.workflows.display.utils.expressions import base_descriptor_validator


def test_mocks__parse_from_app__descriptors():
    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND workflow inputs
    class Inputs(BaseInputs):
        bar: str

    # AND workflow state
    class State(BaseState):
        baz: str

    # AND a workflow class with that Node
    class MyWorkflow(BaseWorkflow[Inputs, State]):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = StartNode.Outputs.foo

    # AND a mock workflow node execution from the app
    raw_mock_workflow_node_executions = [
        {
            "node_id": str(StartNode.__id__),
            "when_condition": {
                "type": "BINARY_EXPRESSION",
                "operator": ">=",
                "lhs": {
                    "type": "EXECUTION_COUNTER",
                    "node_id": str(StartNode.__id__),
                },
                "rhs": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "NUMBER",
                        "value": 1,
                    },
                },
            },
            "then_outputs": {
                "foo": "Hello foo",
            },
        },
        {
            "node_id": str(StartNode.__id__),
            "when_condition": {
                "type": "BINARY_EXPRESSION",
                "operator": "==",
                "lhs": {
                    "type": "WORKFLOW_INPUT",
                    "input_variable_id": str(Inputs.bar.id),
                },
                "rhs": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "STRING",
                        "value": "bar",
                    },
                },
            },
            "then_outputs": {
                "foo": "Hello bar",
            },
        },
        {
            "node_id": str(StartNode.__id__),
            "when_condition": {
                "type": "BINARY_EXPRESSION",
                "operator": "!=",
                "lhs": {
                    "type": "WORKFLOW_STATE",
                    "state_variable_id": str(State.baz.id),
                },
                "rhs": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "STRING",
                        "value": "baz",
                    },
                },
            },
            "then_outputs": {
                "foo": "Hello baz",
            },
        },
    ]

    # WHEN we parsed the raw data on `MockNodeExecution`
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_executions,
        MyWorkflow,
        descriptor_validator=base_descriptor_validator,
    )

    # THEN we get the expected list of MockNodeExecution objects
    assert node_output_mocks
    assert len(node_output_mocks) == 3
    assert node_output_mocks[0] == MockNodeExecution(
        when_condition=StartNode.Execution.count.greater_than_or_equal_to(1),
        then_outputs=StartNode.Outputs(
            foo="Hello foo",
        ),
    )
    assert node_output_mocks[1] == MockNodeExecution(
        when_condition=Inputs.bar.equals("bar"),
        then_outputs=StartNode.Outputs(
            foo="Hello bar",
        ),
    )
    assert node_output_mocks[2] == MockNodeExecution(
        when_condition=State.baz.does_not_equal("baz"),
        then_outputs=StartNode.Outputs(
            foo="Hello baz",
        ),
    )
