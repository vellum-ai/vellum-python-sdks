import pytest
import sys
from uuid import uuid4

from vellum.workflows import BaseInputs, BaseNode, BaseState, BaseWorkflow, MockNodeExecution
from vellum.workflows.exceptions import NodeException
from vellum.workflows.expressions.accessor import AccessorExpression
from vellum.workflows.expressions.add import AddExpression
from vellum.workflows.expressions.and_ import AndExpression
from vellum.workflows.expressions.begins_with import BeginsWithExpression
from vellum.workflows.expressions.between import BetweenExpression
from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
from vellum.workflows.expressions.concat import ConcatExpression
from vellum.workflows.expressions.contains import ContainsExpression
from vellum.workflows.expressions.does_not_begin_with import DoesNotBeginWithExpression
from vellum.workflows.expressions.does_not_contain import DoesNotContainExpression
from vellum.workflows.expressions.does_not_end_with import DoesNotEndWithExpression
from vellum.workflows.expressions.ends_with import EndsWithExpression
from vellum.workflows.expressions.in_ import InExpression
from vellum.workflows.expressions.is_blank import IsBlankExpression
from vellum.workflows.expressions.is_error import IsErrorExpression
from vellum.workflows.expressions.is_not_blank import IsNotBlankExpression
from vellum.workflows.expressions.is_not_null import IsNotNullExpression
from vellum.workflows.expressions.is_null import IsNullExpression
from vellum.workflows.expressions.length import LengthExpression
from vellum.workflows.expressions.minus import MinusExpression
from vellum.workflows.expressions.not_between import NotBetweenExpression
from vellum.workflows.expressions.not_in import NotInExpression
from vellum.workflows.expressions.or_ import OrExpression
from vellum.workflows.expressions.parse_json import ParseJsonExpression
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum_ee.workflows.display.utils.expressions import base_descriptor_validator
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


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


def test_mocks__parse_from_app__when_condition_wraps_dict_without_descriptor_validator():
    """
    Tests that when_condition wraps the original dict in ConstantValueReference when
    descriptor_validator is not provided. This ensures that mocks without a
    descriptor_validator treat the dict as a constant value.
    """

    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow class with that Node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = StartNode.Outputs.foo

    # AND a mock workflow node execution with a when_condition JSON structure
    when_condition_dict = {
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
    }
    raw_mock_workflow_node_executions = [
        {
            "node_id": str(StartNode.__id__),
            "when_condition": when_condition_dict,
            "then_outputs": {
                "foo": "Hello foo",
            },
        },
    ]

    # WHEN we parse the raw data on `MockNodeExecution` without a descriptor_validator
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_executions,
        MyWorkflow,
    )

    # THEN we get a list of MockNodeExecution objects
    assert node_output_mocks is not None
    assert len(node_output_mocks) == 1

    # AND the when_condition wraps the original dict in ConstantValueReference
    assert isinstance(node_output_mocks[0].when_condition, ConstantValueReference)
    assert node_output_mocks[0].when_condition._value == when_condition_dict


def test_mocks__when_condition_dict_with_type_uses_descriptor_validator():
    """
    Tests that a dict with 'type' key uses descriptor_validator from context
    to deserialize into a proper descriptor.
    """

    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow class with that Node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = StartNode.Outputs.foo

    # AND a BINARY_EXPRESSION descriptor representing "1 == 1"
    when_condition_dict = {
        "type": "BINARY_EXPRESSION",
        "operator": "==",
        "lhs": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "NUMBER",
                "value": 1,
            },
        },
        "rhs": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "NUMBER",
                "value": 1,
            },
        },
    }

    # WHEN we create a MockNodeExecution via validate_all with the real descriptor_validator
    node_output_mocks = MockNodeExecution.validate_all(
        [
            {
                "node_id": str(StartNode.__id__),
                "when_condition": when_condition_dict,
                "then_outputs": {
                    "foo": "mocked",
                },
            },
        ],
        MyWorkflow,
        descriptor_validator=base_descriptor_validator,
    )

    # THEN we get a list of MockNodeExecution objects
    assert node_output_mocks is not None
    assert len(node_output_mocks) == 1

    # AND the when_condition is deserialized to an EqualsExpression (not ConstantValueReference)
    from vellum.workflows.expressions.equals import EqualsExpression

    assert isinstance(node_output_mocks[0].when_condition, EqualsExpression)


def test_mocks__use_node_id_from_display():
    """
    Tests that validate_all correctly resolves mocks when the node ID is annotated by the display class.
    """

    # GIVEN a workflow module with a display class that sets a custom node_id
    display_node_id = uuid4()
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode


class StartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        foo: str


class Workflow(BaseWorkflow):
    graph = StartNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = StartNode.Outputs.foo
""",
        "display/__init__.py": """\
# flake8: noqa: F401, F403

from .workflow import *
from .nodes import *
""",
        "display/workflow.py": """\
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    pass
""",
        "display/nodes/__init__.py": """\
# flake8: noqa: F401, F403

from .start_node import *
""",
        "display/nodes/start_node.py": f"""\
from uuid import UUID
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from ...workflow import StartNode


class StartNodeDisplay(BaseNodeDisplay[StartNode]):
    node_id = UUID("{display_node_id}")
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # AND the workflow is loaded from the module
    Workflow = BaseWorkflow.load_from_module(namespace)
    StartNode = list(Workflow.get_nodes())[0]

    # AND a mock workflow node execution using the display-annotated node ID
    raw_mock_workflow_node_executions = [
        {
            "node_id": str(display_node_id),
            "when_condition": {
                "type": "BINARY_EXPRESSION",
                "operator": ">=",
                "lhs": {
                    "type": "EXECUTION_COUNTER",
                    "node_id": str(display_node_id),
                },
                "rhs": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "NUMBER",
                        "value": 0,
                    },
                },
            },
            "then_outputs": {
                "foo": "Hello",
            },
        },
    ]

    # WHEN we parse the mock workflow node execution
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_executions,
        Workflow,
        descriptor_validator=base_descriptor_validator,
    )

    # THEN we get the expected list of MockNodeExecution objects
    assert node_output_mocks
    assert len(node_output_mocks) == 1
    assert node_output_mocks[0] == MockNodeExecution(
        when_condition=StartNode.Execution.count.greater_than_or_equal_to(0),
        then_outputs=StartNode.Outputs(  # type: ignore[call-arg]
            foo="Hello",
        ),
    )


def test_mocks__node_not_found_in_workflow_skips_with_warning(caplog):
    """
    Tests that when a mock references a node_id that doesn't exist in the workflow,
    the mock is skipped with a warning instead of raising an error.
    """

    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow class with that Node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = StartNode.Outputs.foo

    # AND a mock workflow node execution referencing a non-existent node_id
    non_existent_node_id = uuid4()
    raw_mock_with_missing_node = [
        {
            "node_id": str(non_existent_node_id),
            "when_condition": {
                "type": "BINARY_EXPRESSION",
                "operator": ">=",
                "lhs": {
                    "type": "EXECUTION_COUNTER",
                    "node_id": str(non_existent_node_id),
                },
                "rhs": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "NUMBER",
                        "value": 0,
                    },
                },
            },
            "then_outputs": {
                "foo": "Hello",
            },
        }
    ]

    # WHEN we parse the mock workflow node execution
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_with_missing_node,
        MyWorkflow,
        descriptor_validator=base_descriptor_validator,
    )

    # THEN we get an empty list (the mock was skipped)
    assert node_output_mocks == []

    # AND a warning was logged
    assert any(
        f"Skipping mock for node {non_existent_node_id}" in record.message
        and "node not found in workflow MyWorkflow" in record.message
        for record in caplog.records
    )


def test_base_descriptor_validator__vellum_secret():
    """
    Tests that VELLUM_SECRET descriptor type is correctly validated.
    """

    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND a VELLUM_SECRET descriptor
    raw_descriptor = {
        "type": "VELLUM_SECRET",
        "vellum_secret_name": "my_secret",
    }

    # WHEN we validate the descriptor
    result = base_descriptor_validator(raw_descriptor, MyWorkflow)

    # THEN we get a VellumSecretReference
    assert isinstance(result, VellumSecretReference)
    assert result.name == "my_secret"


def test_base_descriptor_validator__environment_variable():
    """
    Tests that ENVIRONMENT_VARIABLE descriptor type is correctly validated.
    """

    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND an ENVIRONMENT_VARIABLE descriptor
    raw_descriptor = {
        "type": "ENVIRONMENT_VARIABLE",
        "environment_variable": "MY_ENV_VAR",
    }

    # WHEN we validate the descriptor
    result = base_descriptor_validator(raw_descriptor, MyWorkflow)

    # THEN we get an EnvironmentVariableReference
    assert isinstance(result, EnvironmentVariableReference)
    assert result.name == "MY_ENV_VAR"


def test_base_descriptor_validator__array_reference():
    """
    Tests that ARRAY_REFERENCE descriptor type is correctly validated.
    """

    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND an ARRAY_REFERENCE descriptor with constant values
    raw_descriptor = {
        "type": "ARRAY_REFERENCE",
        "items": [
            {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "item1"}},
            {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "item2"}},
        ],
    }

    # WHEN we validate the descriptor
    result = base_descriptor_validator(raw_descriptor, MyWorkflow)

    # THEN we get a ConstantValueReference containing a list
    assert isinstance(result, ConstantValueReference)
    assert isinstance(result._value, list)
    assert len(result._value) == 2


def test_base_descriptor_validator__dictionary_reference():
    """
    Tests that DICTIONARY_REFERENCE descriptor type is correctly validated.
    """

    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND a DICTIONARY_REFERENCE descriptor
    raw_descriptor = {
        "type": "DICTIONARY_REFERENCE",
        "entries": [
            {
                "id": "entry1",
                "key": "key1",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "value1"}},
            },
            {
                "id": "entry2",
                "key": "key2",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 42}},
            },
        ],
    }

    # WHEN we validate the descriptor
    result = base_descriptor_validator(raw_descriptor, MyWorkflow)

    # THEN we get a ConstantValueReference containing a dict
    assert isinstance(result, ConstantValueReference)
    assert isinstance(result._value, dict)
    assert "key1" in result._value
    assert "key2" in result._value


@pytest.mark.parametrize(
    "operator,expected_type",
    [
        ("blank", IsBlankExpression),
        ("notBlank", IsNotBlankExpression),
        ("null", IsNullExpression),
        ("notNull", IsNotNullExpression),
        ("isError", IsErrorExpression),
        ("length", LengthExpression),
        ("parseJson", ParseJsonExpression),
    ],
)
def test_base_descriptor_validator__unary_expression(operator, expected_type):
    """
    Tests that UNARY_EXPRESSION descriptor types are correctly validated.
    """

    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND a UNARY_EXPRESSION descriptor
    raw_descriptor = {
        "type": "UNARY_EXPRESSION",
        "operator": operator,
        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "test"}},
    }

    # WHEN we validate the descriptor
    result = base_descriptor_validator(raw_descriptor, MyWorkflow)

    # THEN we get the expected expression type
    assert isinstance(result, expected_type)


@pytest.mark.parametrize(
    "operator,expected_type",
    [
        ("between", BetweenExpression),
        ("notBetween", NotBetweenExpression),
    ],
)
def test_base_descriptor_validator__ternary_expression(operator, expected_type):
    """
    Tests that TERNARY_EXPRESSION descriptor types are correctly validated.
    """

    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND a TERNARY_EXPRESSION descriptor
    raw_descriptor = {
        "type": "TERNARY_EXPRESSION",
        "operator": operator,
        "base": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 5}},
        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 1}},
        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 10}},
    }

    # WHEN we validate the descriptor
    result = base_descriptor_validator(raw_descriptor, MyWorkflow)

    # THEN we get the expected expression type
    assert isinstance(result, expected_type)


@pytest.mark.parametrize(
    "operator,expected_type",
    [
        ("=", BeginsWithExpression.__bases__[0].__bases__[0]),
        ("==", BeginsWithExpression.__bases__[0].__bases__[0]),
        ("doesNotContain", DoesNotContainExpression),
        ("doesNotBeginWith", DoesNotBeginWithExpression),
        ("doesNotEndWith", DoesNotEndWithExpression),
        ("in", InExpression),
        ("notIn", NotInExpression),
        ("and", AndExpression),
        ("or", OrExpression),
        ("coalesce", CoalesceExpression),
        ("+", AddExpression),
        ("-", MinusExpression),
        ("concat", ConcatExpression),
    ],
)
def test_base_descriptor_validator__binary_expression_additional_operators(operator, expected_type):
    """
    Tests that additional BINARY_EXPRESSION operators are correctly validated.
    """

    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND a BINARY_EXPRESSION descriptor with the given operator
    raw_descriptor = {
        "type": "BINARY_EXPRESSION",
        "operator": operator,
        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "left"}},
        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "right"}},
    }

    # WHEN we validate the descriptor
    result = base_descriptor_validator(raw_descriptor, MyWorkflow)

    # THEN we get the expected expression type
    assert isinstance(result, expected_type)


def test_base_descriptor_validator__accessor_expression():
    """
    Tests that accessField operator in BINARY_EXPRESSION is correctly validated.
    """

    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND a BINARY_EXPRESSION descriptor with accessField operator
    raw_descriptor = {
        "type": "BINARY_EXPRESSION",
        "operator": "accessField",
        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": {"field": "value"}}},
        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "field"}},
    }

    # WHEN we validate the descriptor
    result = base_descriptor_validator(raw_descriptor, MyWorkflow)

    # THEN we get an AccessorExpression
    assert isinstance(result, AccessorExpression)


def test_mocks__validate_all__node_nested_in_subworkflow():
    """
    Tests that MockNodeExecution.validate_all correctly handles mocks for nodes
    nested within a subworkflow node by validating against the inner subworkflow.
    """

    # GIVEN a node that will be nested inside a subworkflow
    class NestedNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

        def run(self) -> Outputs:
            raise NodeException("This node should be mocked")

    # AND a subworkflow containing that nested node
    class InnerSubworkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = NestedNode

        class Outputs(BaseWorkflow.Outputs):
            inner_result = NestedNode.Outputs.result

    # AND a subworkflow node that uses the inner subworkflow
    class SubworkflowNode(InlineSubworkflowNode):
        subworkflow = InnerSubworkflow

    # AND an outer workflow containing the subworkflow node
    class OuterWorkflow(BaseWorkflow):
        graph = SubworkflowNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = SubworkflowNode.Outputs.inner_result

    # AND raw mock data for the nested node using the modern data model format
    raw_mock_workflow_node_executions = [
        {
            "node_id": str(NestedNode.__id__),
            "when_condition": {
                "type": "BINARY_EXPRESSION",
                "operator": ">=",
                "lhs": {
                    "type": "EXECUTION_COUNTER",
                    "node_id": str(NestedNode.__id__),
                },
                "rhs": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "NUMBER",
                        "value": 0,
                    },
                },
            },
            "then_outputs": {
                "result": "mocked_result",
            },
        }
    ]

    # WHEN we call validate_all on the outer workflow
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_executions,
        OuterWorkflow,
        descriptor_validator=base_descriptor_validator,
    )

    # THEN we get a list of MockNodeExecution objects
    assert node_output_mocks is not None
    assert len(node_output_mocks) == 1

    # AND the mock is correctly parsed with the nested node's outputs
    assert node_output_mocks[0] == MockNodeExecution(
        when_condition=NestedNode.Execution.count.greater_than_or_equal_to(0),
        then_outputs=NestedNode.Outputs(result="mocked_result"),
    )

    # AND when we run the outer workflow with the mocks
    workflow = OuterWorkflow()
    terminal_event = workflow.run(node_output_mocks=node_output_mocks)

    # THEN the workflow completes successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output reflects the mocked value from the nested node
    assert terminal_event.outputs.final_result == "mocked_result"


def test_mocks__serialize__try_node_wrapped_node_has_correct_node_id():
    """
    Tests that when serializing a MockNodeExecution for a node wrapped in a TryNode adornment,
    the serialized node_id matches the inner wrapped node's ID (not the adornment wrapper's ID).
    """

    # GIVEN a node wrapped in a TryNode adornment
    @TryNode.wrap()
    class WrappedNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    # AND a workflow that uses the wrapped node
    class MyWorkflow(BaseWorkflow):
        graph = WrappedNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = WrappedNode.Outputs.result

    # AND a mock for the wrapped node
    mock = MockNodeExecution(
        when_condition=ConstantValueReference(True),
        then_outputs=WrappedNode.Outputs(result="mocked_result"),
    )

    # WHEN we serialize the mock
    serialized_mock = mock.model_dump()

    # THEN the serialized node_id should match the inner wrapped node's ID
    inner_node = WrappedNode.__wrapped_node__
    assert inner_node is not None
    assert serialized_mock["node_id"] == str(inner_node.__id__)

    # AND the serialized mock should have the correct type
    assert serialized_mock["type"] == "NODE_EXECUTION"

    # AND the then_outputs should be serialized correctly
    assert serialized_mock["then_outputs"]["result"] == "mocked_result"


def test_mocks__validate_all__try_node_wrapped_node_deserializes_correctly():
    """
    Tests that validate_all correctly deserializes a mock for a node wrapped in a TryNode adornment.
    """

    # GIVEN a node wrapped in a TryNode adornment
    @TryNode.wrap()
    class WrappedNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    # AND a workflow that uses the wrapped node
    class MyWorkflow(BaseWorkflow):
        graph = WrappedNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = WrappedNode.Outputs.result

    # AND the inner wrapped node's ID
    inner_node = WrappedNode.__wrapped_node__
    assert inner_node is not None

    # AND a raw mock workflow node execution using the inner node's ID
    raw_mock_workflow_node_executions = [
        {
            "node_id": str(inner_node.__id__),
            "when_condition": {
                "type": "BINARY_EXPRESSION",
                "operator": ">=",
                "lhs": {
                    "type": "EXECUTION_COUNTER",
                    "node_id": str(inner_node.__id__),
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
                "result": "mocked_result",
            },
        },
    ]

    # WHEN we parse the raw data on MockNodeExecution
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_executions,
        MyWorkflow,
        descriptor_validator=base_descriptor_validator,
    )

    # THEN we get a list with one MockNodeExecution object
    assert node_output_mocks is not None
    assert len(node_output_mocks) == 1

    # AND the MockNodeExecution has the correct when_condition
    assert node_output_mocks[0].when_condition == inner_node.Execution.count.greater_than_or_equal_to(1)

    # AND the then_outputs is the correct type with the expected value
    assert node_output_mocks[0].then_outputs == inner_node.Outputs(result="mocked_result")


def test_mocks__validate_all__ignores_undefined_outputs():
    """
    Tests that validate_all ignores outputs that are not defined in the node's Outputs class.
    """

    # GIVEN a node wrapped in a TryNode adornment
    @TryNode.wrap()
    class WrappedNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    # AND a workflow that uses the wrapped node
    class MyWorkflow(BaseWorkflow):
        graph = WrappedNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = WrappedNode.Outputs.result

    # AND the inner wrapped node's ID
    inner_node = WrappedNode.__wrapped_node__
    assert inner_node is not None

    # AND a raw mock workflow node execution with an undefined "error" output
    raw_mock_workflow_node_executions = [
        {
            "node_id": str(inner_node.__id__),
            "when_condition": {
                "type": "BINARY_EXPRESSION",
                "operator": ">=",
                "lhs": {
                    "type": "EXECUTION_COUNTER",
                    "node_id": str(inner_node.__id__),
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
                "result": "mocked_result",
                "error": "some error value",
            },
        },
    ]

    # WHEN we parse the raw data on MockNodeExecution
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_executions,
        MyWorkflow,
        descriptor_validator=base_descriptor_validator,
    )

    # THEN we get a list with one MockNodeExecution object
    assert node_output_mocks is not None
    assert len(node_output_mocks) == 1

    # AND the then_outputs only contains the declared "result" output
    assert node_output_mocks[0].then_outputs == inner_node.Outputs(result="mocked_result")

    # AND the "error" output was ignored and is not present
    assert not hasattr(node_output_mocks[0].then_outputs, "error")
