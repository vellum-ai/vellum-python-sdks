import pytest
from dataclasses import dataclass
import os
import shutil
import tempfile
from uuid import uuid4
from typing import Any, Callable, Dict, Generator

import tomli_w


@dataclass
class MockModuleResult:
    temp_dir: str
    module: str
    set_pyproject_toml: Callable[[Dict[str, Any]], None]
    workflow_sandbox_id: str


@pytest.fixture
def mock_module(request) -> Generator[MockModuleResult, None, None]:
    current_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    # Use the test name to create a unique module path
    module = f"examples.mock.{request.node.name}"
    workflow_sandbox_id = str(uuid4())

    def set_pyproject_toml(vellum_config: Dict[str, Any]) -> None:
        pyproject_toml_path = os.path.join(temp_dir, "pyproject.toml")
        with open(pyproject_toml_path, "wb") as f:
            tomli_w.dump(
                {"tool": {"vellum": vellum_config}},
                f,
            )

    set_pyproject_toml(
        {
            "workflows": [
                {
                    "module": module,
                    "workflow_sandbox_id": workflow_sandbox_id,
                }
            ]
        }
    )

    with open(os.path.join(temp_dir, ".env"), "w") as f:
        f.write("VELLUM_API_KEY=abcdef123456")

    yield MockModuleResult(
        temp_dir=temp_dir,
        module=module,
        set_pyproject_toml=set_pyproject_toml,
        workflow_sandbox_id=workflow_sandbox_id,
    )

    os.chdir(current_dir)
    shutil.rmtree(temp_dir)
