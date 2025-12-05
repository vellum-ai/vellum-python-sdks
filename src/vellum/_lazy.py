"""
Lazy loading utility for vellum submodules.

This module provides a helper to defer imports until they're actually accessed,
significantly improving import time for users who only need a subset of the API.
"""

from importlib import import_module
from typing import Callable, Dict, List, Tuple


def make_lazy_loader(
    parent_module_name: str,
    lazy_imports: Dict[str, Tuple[str, str]],
) -> Tuple[Callable[[str], object], Callable[[], List[str]]]:
    """
    Create __getattr__ and __dir__ functions for lazy module loading.

    Args:
        parent_module_name: The __name__ of the module using this loader (e.g., "vellum.workflows")
        lazy_imports: A dict mapping attribute names to (submodule, attr_name) tuples.
                      Example: {"BaseInputs": (".inputs", "BaseInputs")}

    Returns:
        A tuple of (__getattr__, __dir__) functions to assign in the module.

    Usage:
        # In your __init__.py:
        from vellum._lazy import make_lazy_loader

        _LAZY_IMPORTS = {
            "BaseInputs": (".inputs", "BaseInputs"),
            "BaseNode": (".nodes", "BaseNode"),
        }

        __getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)
        __all__ = list(_LAZY_IMPORTS.keys())
    """
    # Cache for already-imported attributes
    _cache: Dict[str, object] = {}

    def __getattr__(name: str) -> object:
        if name in _cache:
            return _cache[name]

        if name not in lazy_imports:
            raise AttributeError(f"module {parent_module_name!r} has no attribute {name!r}")

        submodule_path, attr_name = lazy_imports[name]
        module = import_module(submodule_path, parent_module_name)
        value = getattr(module, attr_name)

        # Cache the value so subsequent accesses are fast
        _cache[name] = value
        return value

    def __dir__() -> List[str]:
        # Include lazy imports + any module-level names
        return list(lazy_imports.keys())

    return __getattr__, __dir__
