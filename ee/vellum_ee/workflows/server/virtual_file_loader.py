import importlib


class VirtualFileLoader(importlib.abc.Loader):
    def __init__(self, code: str, is_package: bool):
        self.code = code
        self.is_package = is_package

    def create_module(self, spec):
        return None  # use default module creation

    def exec_module(self, module):
        if not self.is_package or self.code:
            exec(self.code, module.__dict__)


class VirtualFileFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, files: dict[str, str], namespace: str):
        self.files = files
        self.namespace = namespace

    def find_spec(self, fullname, path, target=None):
        # Do the namespacing on the fly to avoid having to copy the file dict
        prefixed_name = fullname if fullname.startswith(self.namespace) else f"{self.namespace}.{fullname}"

        key_name = "__init__" if fullname == self.namespace else fullname.replace(f"{self.namespace}.", "")

        files_key = f"{key_name.replace('.', '/')}.py"
        if self.files.get(files_key) is None:
            files_key = f"{key_name.replace('.', '/')}/__init__.py"

        file = self.files.get(files_key)
        is_package = "__init__" in files_key

        if file is not None:
            return importlib.machinery.ModuleSpec(
                prefixed_name,
                VirtualFileLoader(file, is_package),
                origin=prefixed_name,
                is_package=is_package,
            )
        return None
