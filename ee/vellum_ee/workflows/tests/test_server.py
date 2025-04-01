import pytest
import sys
from uuid import uuid4
from typing import Type, cast

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


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


@pytest.mark.skip(reason="Code execution inspect and get read file from path needs to be fixed")
def test_load_from_module__ts_code_in_file_loader():
    # GIVEN a workflow module with only a code execution node
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

class CodeExecutionNode(BaseCodeExecutionNode[BaseState, Any]):
    filepath = "./script.ts"
    code_inputs = {}
    runtime = "TYPESCRIPT_5_3_3"
    packages = []
""",
        "nodes/code_execution_node/script.ts": """async function main(inputs: {
  text: string,
}): any {
  const matches = inputs.text.match(/\\((.+?)\\)/gs);
  return matches;
}""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # WHEN the workflow is loaded
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow()

    # THEN the workflow is successfully initialized
    assert workflow

    event = workflow.run()
    assert event.name == "workflow.execution.fulfilled"
