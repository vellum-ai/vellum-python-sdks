import pytest
import importlib
import os
import sys
from uuid import uuid4

from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


@pytest.fixture
def files() -> dict[str, str]:
    base_directory = os.path.join(os.path.dirname(__file__), "local_files")
    files = {}

    for root, _, filenames in os.walk(base_directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            # Key will be the relative path inside `local_files`
            relative_path = str(os.path.relpath(file_path, start=base_directory))
            with open(file_path, encoding="utf-8") as f:
                files[relative_path] = f.read()

    return files


def test_base_class_dynamic_import(files):
    """
    Test dynamically importing the base class and ensuring all required modules are loaded.
    """
    namespace = str(uuid4())  # Create a unique namespace
    sys.meta_path.append(VirtualFileFinder(files, namespace))  # Use virtual file loader
    base_class_module_path = "base_class.py"

    # When given a valid module path
    assert base_class_module_path in files, f"{base_class_module_path} is missing from local_files"

    # fully qualified module name for the base class
    full_module_name = f"{namespace}.base_class"

    # sys.modules keys before import
    existing_modules = set(sys.modules.keys())

    # If we import the base module (should implicitly load its dependencies)
    base_class_module = importlib.import_module(full_module_name)
    assert base_class_module, f"Failed to import module: {full_module_name}"

    baseclass = None
    for name in dir(base_class_module):
        if name.startswith("__"):
            continue
        obj = getattr(base_class_module, name)
        if isinstance(obj, type):
            baseclass = obj
            break

    assert baseclass
    # Then we should import all required files
    new_modules = set(sys.modules.keys()) - existing_modules
    assert new_modules

    required_modules = [
        "uuid",
        f"{namespace}",
        f"{namespace}.base_class",
        f"{namespace}.inner_files",
        f"{namespace}.inner_files.inner_class",
        f"{namespace}.display",
        f"{namespace}.display.display",
    ]
    for module in required_modules:
        assert module in sys.modules, f"Module '{module}' was not loaded as expected"

    # Verify that BaseClass can be instantiated without missing imports
    try:
        instance = baseclass()
        assert instance, "Failed to instantiate BaseClass"

        results = instance.run()
        assert results, "Failed to run BaseClass"
        assert instance.id
    except Exception as e:
        pytest.fail(f"Failed to create an instance of BaseClass: {e}")


def test_display_directory_not_auto_generated():
    """
    Test that display directories are NOT auto-generated with empty __init__.py files.
    Display directories typically have specific __init__.py content (e.g., "from .workflow import *")
    that should not be replaced with empty auto-generated files.
    """
    # GIVEN a workflow with display/workflow.py but NO display/__init__.py
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode

class StartNode(BaseNode):
    pass

class Workflow(BaseWorkflow):
    graph = StartNode
""",
        "display/workflow.py": """\
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

class WorkflowDisplay(BaseWorkflowDisplay):
    pass
""",
        # Note: NO "display/__init__.py" in files dict
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    try:
        # WHEN we try to resolve display/__init__.py
        # (This is what happens internally when trying to import the display module)
        import importlib.util

        spec = importlib.util.find_spec(f"{namespace}.display")

        # THEN the spec should be None because we don't want to auto-generate display/__init__.py
        # If the spec exists, it means an empty __init__.py was auto-generated (BAD)
        assert spec is None, (
            "display directory should NOT have auto-generated __init__.py. "
            "Display directories require specific __init__.py content that shouldn't be empty."
        )

    finally:
        # Clean up
        sys.meta_path = [finder for finder in sys.meta_path if not isinstance(finder, VirtualFileFinder)]


def test_nested_display_directory_not_auto_generated():
    """
    Test that nested display directories (e.g., nodes/subworkflow/display/) are also excluded
    from auto-generation. This catches cases where display directories appear inside
    subworkflows or map nodes.
    """
    # GIVEN a workflow with nested display directory but NO display/__init__.py
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode

class StartNode(BaseNode):
    pass

class Workflow(BaseWorkflow):
    graph = StartNode
""",
        "nodes/subworkflow/workflow.py": """\
from vellum.workflows import BaseWorkflow

class SubworkflowWorkflow(BaseWorkflow):
    pass
""",
        "nodes/subworkflow/display/workflow.py": """\
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

class SubworkflowWorkflowDisplay(BaseWorkflowDisplay):
    pass
""",
        # Note: NO "nodes/subworkflow/display/__init__.py" in files dict
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    try:
        # WHEN we try to resolve nodes.subworkflow.display.__init__.py
        import importlib.util

        spec = importlib.util.find_spec(f"{namespace}.nodes.subworkflow.display")

        # THEN the spec should be None because nested display directories should also be excluded
        assert spec is None, (
            "Nested display directory (nodes/subworkflow/display/) should NOT have "
            "auto-generated __init__.py. Display directories at any nesting level require "
            "specific __init__.py content that shouldn't be empty."
        )

    finally:
        # Clean up
        sys.meta_path = [finder for finder in sys.meta_path if not isinstance(finder, VirtualFileFinder)]
