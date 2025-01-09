import pytest
import importlib
import os
import sys
from uuid import uuid4

from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


@pytest.fixture
def files() -> dict[str, str]:
    base_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_files")
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

    # Identify the module containing the base class
    base_class_module_path = "base_class.py"

    # Validate that the required file exists in `local_files`
    assert base_class_module_path in files, f"{base_class_module_path} is missing from local_files"

    # Expected fully qualified module name for the base class
    full_module_name = f"{namespace}.base_class"

    # Track sys.modules keys before import
    existing_modules = set(sys.modules.keys())

    # Import the base module (should implicitly load its dependencies)
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
    # Check for required modules by comparing sys.modules
    new_modules = set(sys.modules.keys()) - existing_modules
    assert new_modules

    # Example check (validate specific dependencies if known)
    required_modules = [
        "uuid",
        f"{namespace}",
        f"{namespace}.base_class",
        f"{namespace}.inner_files",
        f"{namespace}.inner_files.inner_class",
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
