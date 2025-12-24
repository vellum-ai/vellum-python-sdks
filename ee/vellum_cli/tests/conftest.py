import pytest
from dataclasses import dataclass
import pathlib
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
def mock_module(
    request, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> Generator[MockModuleResult, None, None]:
    monkeypatch.chdir(tmp_path)

    # Use the test name to create a unique module path
    module = f"examples.mock.{request.node.name}"
    workflow_sandbox_id = str(uuid4())

    def set_pyproject_toml(vellum_config: Dict[str, Any]) -> None:
        pyproject_toml_path = tmp_path / "pyproject.toml"
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

    with open(tmp_path / ".env", "w") as f:
        f.write("VELLUM_API_KEY=abcdef123456")

    yield MockModuleResult(
        temp_dir=str(tmp_path),
        module=module,
        set_pyproject_toml=set_pyproject_toml,
        workflow_sandbox_id=workflow_sandbox_id,
    )


@pytest.fixture
def info_log_level(monkeypatch):
    """Set log level to INFO for tests that request this fixture"""
    monkeypatch.setenv("LOG_LEVEL", "INFO")
