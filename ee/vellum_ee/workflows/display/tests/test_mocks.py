import sys
from uuid import uuid4

from vellum.workflows import BaseInputs, BaseNode, BaseState, BaseWorkflow, MockNodeExecution
from vellum.workflows.references.constant import ConstantValueReference
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


def test_mocks__parse_from_app__when_condition_defaults_to_false_without_descriptor_validator():
    """
    Tests that when_condition defaults to ConstantValueReference(False) when
    descriptor_validator is not provided. This ensures that mocks without a
    descriptor_validator have a valid when_condition that evaluates to False.
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

    # AND a mock workflow node execution with a valid when_condition JSON structure
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
    ]

    # WHEN we parse the raw data on `MockNodeExecution` without a descriptor_validator
    node_output_mocks = MockNodeExecution.validate_all(
        raw_mock_workflow_node_executions,
        MyWorkflow,
    )

    # THEN we get a list of MockNodeExecution objects
    assert node_output_mocks is not None
    assert len(node_output_mocks) == 1

    # AND the when_condition defaults to ConstantValueReference(False)
    assert node_output_mocks[0].when_condition == ConstantValueReference(False)


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
