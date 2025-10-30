import importlib
from importlib.machinery import ModuleSpec
import re
import sys
from typing import Optional

from vellum.workflows.loaders.base import BaseWorkflowFinder


class VirtualFileLoader(importlib.abc.Loader):
    def __init__(self, files: dict[str, str], namespace: str, source_module: Optional[str] = None):
        self.files = files
        self.namespace = namespace
        self.source_module = source_module

    def create_module(self, spec: ModuleSpec):
        """
        We started with cpython/Lib/importlib/_bootstrap.py::FrozenImporter::create_module here

        https://github.com/python/cpython/blob/053c285f6b41f92fbdd1d4ff0c959cceefacd7cd/Lib/importlib/_bootstrap.py#L1160C1-L1169C22

        and reduced our needs to just updating the __file__ attribute directly.
        """
        module = type(sys)(spec.name)
        module.__file__ = spec.origin
        return module

    def exec_module(self, module):
        module_info = self._resolve_module(module.__spec__.name)

        if module_info:
            file_path, code = module_info
            namespaced_path = (
                file_path if file_path.startswith(f"{self.namespace}/") else f"{self.namespace}/{file_path}"
            )
            module.__file__ = namespaced_path
            compiled = compile(code, namespaced_path, "exec")
            exec(compiled, module.__dict__)

    def get_source(self, fullname):
        """
        `inspect` module uses this method to get the source code of a module.
        """

        module_info = self._resolve_module(fullname)
        if module_info:
            return module_info[1]

        return None

    def _resolve_module(self, fullname: str) -> Optional[tuple[str, str]]:
        file_path = self._get_file_path(fullname)
        code = self._get_code(file_path)

        if code is not None:
            return file_path, code

        if not file_path.endswith("__init__.py"):
            file_path = re.sub(r"\.py$", "/__init__.py", file_path)
            code = self._get_code(file_path)

            if code is not None:
                return file_path, code

            relative_name = self._to_relative(fullname)
            if relative_name is not None and self._is_package_directory(relative_name):
                return self._generate_init_content(relative_name)

        return None

    def _to_relative(self, fullname: str) -> Optional[str]:
        """Convert a fully qualified module name to a relative name without the namespace prefix."""
        if fullname.startswith(self.namespace + "."):
            return fullname[len(self.namespace) + 1 :]
        elif fullname == self.namespace:
            return ""
        return None

    def _get_file_path(self, fullname):
        return f"{fullname.replace('.', '/')}.py"

    def _get_code(self, file_path):
        file_key_name = re.sub(r"^" + re.escape(self.namespace) + r"/", "", file_path)
        return self.files.get(file_key_name)

    def _is_package_directory(self, fullname: str) -> bool:
        """Check if directory contains .py files that should be treated as a package."""
        directory_prefix = fullname.replace(".", "/") + "/"

        # Exclude display directories from auto-generation as they typically have
        # specific __init__.py content that shouldn't be replaced with empty files
        if directory_prefix.startswith("display/"):
            return False

        for file_path in self.files.keys():
            if file_path.startswith(directory_prefix):
                if file_path.endswith(".py") and not file_path.endswith("__init__.py"):
                    return True
                remaining_path = file_path[len(directory_prefix) :]
                if "/" in remaining_path:
                    return True

        return False

    def _generate_init_content(self, fullname: str) -> tuple[str, str]:
        """Auto-generate empty __init__.py content to mark directory as a package."""
        directory_prefix = fullname.replace(".", "/") + "/"
        file_path = directory_prefix + "__init__.py"

        code = ""

        return file_path, code


class VirtualFileFinder(BaseWorkflowFinder):
    def __init__(self, files: dict[str, str], namespace: str, source_module: Optional[str] = None):
        self.loader = VirtualFileLoader(files, namespace, source_module)
        self.source_module = source_module
        self.namespace = namespace

    def format_error_message(self, error_message: str) -> str:
        """Format error message by replacing namespace with source_module."""
        if self.source_module and self.namespace in error_message:
            return error_message.replace(self.namespace, self.source_module)
        return error_message

    def find_spec(self, fullname: str, path, target=None):
        module_info = self.loader._resolve_module(fullname)
        if module_info:
            file_path, _ = module_info
            is_package = file_path.endswith("__init__.py")
            return importlib.machinery.ModuleSpec(
                fullname,
                self.loader,
                origin=file_path,
                is_package=is_package,
            )

        return None
