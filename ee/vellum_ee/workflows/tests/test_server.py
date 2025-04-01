import pytest
import sys
from uuid import uuid4
from typing import Type, cast

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.code_executor_response import CodeExecutorResponse
from vellum.client.types.number_vellum_value import NumberVellumValue
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


@pytest.fixture
def mock_open(mocker):
    return mocker.patch("vellum.workflows.nodes.displayable.code_execution_node.utils.open")


def test_load_workflow_event_display_context():
    # DEPRECATED: Use `vellum.workflows.events.workflow.WorkflowEventDisplayContext` instead. Will be removed in 0.15.0
    from vellum_ee.workflows.display.types import WorkflowEventDisplayContext

    # We are actually just ensuring there are no circular dependencies when
    # our Workflow Server imports this class.
    assert issubclass(WorkflowEventDisplayContext, UniversalBaseModel)


def test_load_from_module__lazy_reference_in_file_loader():
    # GIVEN a workflow module with a node containing a lazy reference
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.start_node import StartNode

class Workflow(BaseWorkflow):
    graph = StartNode
""",
        "nodes/__init__.py": """\
from .start_node import StartNode

__all__ = [
    "StartNode",
]
""",
        "nodes/start_node.py": """\
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references import LazyReference

class StartNode(BaseNode):
    foo = LazyReference(lambda: StartNode.Outputs.bar)

    class Outputs(BaseNode.Outputs):
        bar = str
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow()

    # THEN the workflow is successfully initialized
    assert workflow

    # AND the graph is just a BaseNode
    # ideally this would be true, but the loader uses a different BaseNode class definition than
    # the one in this test module.
    # assert isinstance(workflow.graph, BaseNode)
    start_node = cast(Type[BaseNode], workflow.graph)
    assert start_node.__bases__ == (BaseNode,)

    # AND the lazy reference has the correct name
    assert start_node.foo.instance
    assert start_node.foo.instance.name == "StartNode.Outputs.bar"


def test_load_from_module__ts_code_in_file_loader(
    mock_open,
    vellum_client,
):
    # GIVEN typescript code
    ts_code = """async function main(): any {
  return 5;
}"""

    # AND a workflow module with only a code execution node
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.code_execution_node import CodeExecutionNode

class Workflow(BaseWorkflow):
    graph = CodeExecutionNode
""",
        "nodes/__init__.py": """\
from .code_execution_node import CodeExecutionNode

__all__ = ["CodeExecutionNode"]
""",
        "nodes/code_execution_node.py": """\
from typing import Any

from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode
from vellum.workflows.state import BaseState

class CodeExecutionNode(BaseCodeExecutionNode[BaseState, int]):
    filepath = "./script.ts"
    code_inputs = {}
    runtime = "TYPESCRIPT_5_3_3"
    packages = []
""",
        "nodes/code_execution_node/script.ts": ts_code,
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # AND the open function returns our file content
    mock_open.return_value.__enter__.return_value.read.return_value = ts_code

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow()

    # THEN the workflow is successfully initialized
    assert workflow

    event = workflow.run()
    assert event.name == "workflow.execution.fulfilled", event.model_dump_json()

    # AND we pass in the correct file path to the open function
    assert mock_open.call_args[0][0] == f"{namespace}/nodes/./script.ts"

    # AND we invoke the Code Execution Node with the correct code
    assert vellum_client.execute_code.call_args.kwargs["code"] == ts_code
