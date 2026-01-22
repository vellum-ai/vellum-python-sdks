import pytest
import sys
from uuid import uuid4

from vellum.workflows import BaseWorkflow
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


@pytest.fixture
def virtual_file_loader():
    """Fixture to manage VirtualFileFinder registration and cleanup."""
    finders = []

    def _register(files, namespace, source_module=None):
        finder = VirtualFileFinder(files, namespace, source_module=source_module)
        sys.meta_path.append(finder)
        finders.append(finder)
        return finder

    yield _register

    for finder in reversed(finders):
        if finder in sys.meta_path:
            sys.meta_path.remove(finder)


def test_resolve_node_ref__suffix_matching_with_namespace_prefix(virtual_file_loader):
    """
    Tests that resolve_node_ref correctly resolves node references when the node's
    __module__ has a UUID namespace prefix (as happens with dynamically loaded workflows).

    This tests the fallback path in resolve_node_ref that matches nodes by their
    module path suffix when direct import fails.
    """
    # GIVEN a workflow with nodes in a subpackage
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.my_node import MyNode

class Workflow(BaseWorkflow):
    graph = MyNode
""",
        "nodes/__init__.py": "from .my_node import MyNode",
        "nodes/my_node.py": """\
from vellum.workflows.nodes import BaseNode

class MyNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        greeting: str

    def run(self) -> Outputs:
        return self.Outputs(greeting="Hello, World!")
""",
    }

    # AND the workflow is loaded with a UUID namespace (simulating dynamic loading)
    namespace = str(uuid4())
    virtual_file_loader(files, namespace)

    # WHEN we load the workflow
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow()

    # Verify the node's __module__ has the namespace prefix
    MyNode = workflow.graph
    assert MyNode.__module__.startswith(namespace)
    assert MyNode.__module__ == f"{namespace}.nodes.my_node"

    # AND we call run_node with the module path string (without namespace prefix)
    # This is how the API passes node references: "nodes.my_node.MyNode"
    # The direct import will fail because "nodes.my_node" doesn't exist at the top level,
    # so resolve_node_ref falls back to suffix matching
    events = list(workflow.run_node("nodes.my_node.MyNode"))

    # THEN the node should execute successfully
    assert len(events) >= 2  # At least initiated and fulfilled events

    # AND the last event should be a fulfilled event with the correct output
    fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    assert len(fulfilled_events) == 1

    outputs = fulfilled_events[0].outputs
    assert outputs.greeting == "Hello, World!"
