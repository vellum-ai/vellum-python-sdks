import importlib
import re
from typing import Optional


class VirtualFileLoader(importlib.abc.Loader):
    def __init__(self, files: dict[str, str], namespace: str):
        self.files = files
        self.namespace = namespace

    def create_module(self, spec):
        return None  # use default module creation

    def exec_module(self, module):
        module_info = self._resolve_module(module.__spec__.origin)

        if module_info:
            file_path, code = module_info
            compiled = compile(code, file_path, "exec")
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

        return None

    def _get_file_path(self, fullname):
        return f"{fullname.replace('.', '/')}.py"

    def _get_code(self, file_path):
        file_key_name = re.sub(r"^" + re.escape(self.namespace) + r"/", "", file_path)
        return self.files.get(file_key_name)


class VirtualFileFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, files: dict[str, str], namespace: str):
        self.loader = VirtualFileLoader(files, namespace)

    def find_spec(self, fullname: str, path, target=None):
        module_info = self.loader._resolve_module(fullname)
        if module_info:
            file_path, _ = module_info
            is_package = file_path.endswith("__init__.py")
            return importlib.machinery.ModuleSpec(
                fullname,
                self.loader,
                origin=fullname,
                is_package=is_package,
            )
        return None
