import pytest
import sys
from uuid import uuid4

from vellum.workflows import BaseWorkflow
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


@pytest.fixture
def virtual_file_loader():
    """Fixture to manage VirtualFileFinder registration and cleanup."""
    finders = []
    namespaces = []
    file_modules = []  # Track module names derived from file paths

    def _register(files, namespace, source_module=None):
        finder = VirtualFileFinder(files, namespace, source_module=source_module)
        # Insert at beginning to ensure our finder takes priority
        sys.meta_path.insert(0, finder)
        finders.append(finder)
        namespaces.append(namespace)

        # Track module names that could be created from the file paths
        # The VirtualFileFinder can respond to imports without the namespace prefix
        for file_path in files.keys():
            if file_path.endswith(".py") and file_path != "__init__.py":
                # Convert file path to module name (e.g., "nodes/my_node.py" -> "nodes.my_node")
                module_name = file_path[:-3].replace("/", ".")
                file_modules.append(module_name)
                # Also track parent packages (e.g., "nodes")
                parts = module_name.split(".")
                for i in range(1, len(parts)):
                    file_modules.append(".".join(parts[:i]))

        return finder

    yield _register

    # Clean up finders from sys.meta_path
    for finder in reversed(finders):
        if finder in sys.meta_path:
            sys.meta_path.remove(finder)

    # Clean up loaded modules from sys.modules to avoid caching issues
    for namespace in namespaces:
        modules_to_remove = [key for key in sys.modules if key.startswith(namespace)]
        for mod in modules_to_remove:
            del sys.modules[mod]

    # Also clean up any modules created without the namespace prefix
    # (due to VirtualFileFinder responding to non-prefixed imports)
    for mod in file_modules:
        if mod in sys.modules:
            del sys.modules[mod]


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
        "nodes/__init__.py": "",
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


def test_resolve_node_ref__node_with_relative_imports(virtual_file_loader):
    """
    Tests that run_node works when the node file itself has relative imports
    to sibling modules within the same subpackage.
    """
    # GIVEN a workflow where the node imports from a relative module
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.my_node import MyNode

class Workflow(BaseWorkflow):
    graph = MyNode
""",
        "nodes/__init__.py": "",
        "nodes/my_node.py": """\
from vellum.workflows.nodes import BaseNode
from .helpers import get_greeting

class MyNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        greeting: str

    def run(self) -> Outputs:
        return self.Outputs(greeting=get_greeting())
""",
        "nodes/helpers.py": """\
def get_greeting():
    return "Hello from helper!"
""",
    }

    # AND the workflow is loaded with a UUID namespace
    namespace = str(uuid4())
    virtual_file_loader(files, namespace)

    # WHEN we load the workflow and run the node
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow()

    events = list(workflow.run_node("nodes.my_node.MyNode"))

    # THEN the node should execute successfully using the relative import
    fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    assert len(fulfilled_events) == 1

    outputs = fulfilled_events[0].outputs
    assert outputs.greeting == "Hello from helper!"


def test_resolve_node_ref__node_with_relative_import_input_attributes(virtual_file_loader):
    """
    Tests that run_node works when a node has input attributes that use types
    defined via relative imports from sibling modules.
    """
    # GIVEN a workflow where the node has inputs using types from relative imports
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.my_node import MyNode

class Workflow(BaseWorkflow):
    graph = MyNode
""",
        "nodes/__init__.py": "",
        "nodes/my_node.py": """\
from vellum.workflows.nodes import BaseNode
from .types import UserConfig

class MyNode(BaseNode):
    config: UserConfig

    class Outputs(BaseNode.Outputs):
        greeting: str

    def run(self) -> Outputs:
        return self.Outputs(greeting=f"Hello, {self.config.name}!")
""",
        "nodes/types.py": """\
from dataclasses import dataclass

@dataclass
class UserConfig:
    name: str
    enabled: bool = True
""",
    }

    # AND the workflow is loaded with a UUID namespace
    namespace = str(uuid4())
    virtual_file_loader(files, namespace)

    # WHEN we load the workflow and run the node with inputs
    Workflow = BaseWorkflow.load_from_module(namespace)
    workflow = Workflow()

    # Import the UserConfig type from the loaded module to create input
    import importlib

    types_module = importlib.import_module(f"{namespace}.nodes.types")
    UserConfig = types_module.UserConfig

    events = list(workflow.run_node("nodes.my_node.MyNode", inputs={"config": UserConfig(name="World")}))

    # THEN the node should execute successfully using the relatively-imported type
    fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    assert len(fulfilled_events) == 1

    outputs = fulfilled_events[0].outputs
    assert outputs.greeting == "Hello, World!"
