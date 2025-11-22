import pytest
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Dict, List, Tuple

from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def _collect_file_map(root: Path) -> Dict[str, str]:
    """Collect all Python files from a directory tree into a dict mapping relative path to contents."""
    file_map: Dict[str, str] = {}
    for path in root.rglob("*.py"):
        # Skip __pycache__ or other non-source directories
        if "__pycache__" in path.parts:
            continue
        rel_path = str(path.relative_to(root))
        file_map[rel_path] = path.read_text(encoding="utf-8")
    return file_map


def _compute_diff(
    original_root: Path,
    generated_root: Path,
) -> Tuple[List[str], List[str], List[str]]:
    """
    Compare files between original and generated directories.

    Returns:
        Tuple of (original_only, generated_only, modified) file lists
    """
    original_files = _collect_file_map(original_root)
    generated_files = _collect_file_map(generated_root)

    orig_keys = set(original_files.keys())
    gen_keys = set(generated_files.keys())

    original_only = sorted(orig_keys - gen_keys)
    generated_only = sorted(gen_keys - orig_keys)

    modified = sorted(rel for rel in orig_keys & gen_keys if original_files[rel] != generated_files[rel])

    return original_only, generated_only, modified


@pytest.mark.xfail(reason="Zero-diff transforms not yet implemented")
@pytest.mark.parametrize(
    "module_name",
    [
        "trivial",
        "builtin_list_str",
    ],
)
def test_zero_diff_transforms(module_name: str):
    """
    Tests that serializing a workflow, running codegen, and comparing files produces no diff.

    GIVEN a workflow defined in tests.workflows.{module_name}
    WHEN we serialize it to exec_config and run TypeScript codegen on that JSON
    THEN the generated files match the original workflow files (zero diff).
    """

    # GIVEN the original workflow module
    workflow_module = f"tests.workflows.{module_name}"
    original_root = Path(workflow_module.replace(".", os.path.sep))

    # WHEN we serialize the workflow to exec_config
    serialization_result = BaseWorkflowDisplay.serialize_module(workflow_module)
    original_exec_config = serialization_result.exec_config

    # AND we run codegen on the serialized data
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        exec_config_path = temp_dir_path / "exec_config.json"
        exec_config_path.write_text(json.dumps(original_exec_config))

        codegen_dir = Path(__file__).parent.parent / "codegen"
        output_dir = temp_dir_path / "generated"
        output_dir.mkdir()

        env = os.environ.copy()
        env.setdefault("VELLUM_API_KEY", "test-api-key")

        result = subprocess.run(
            [
                "npx",
                "tsx",
                "src/cli.ts",
                "--exec-config",
                str(exec_config_path),
                "--output-dir",
                str(output_dir),
                "--module-name",
                module_name,
            ],
            cwd=str(codegen_dir),
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, f"Codegen failed: {result.stderr}"

        # Find the generated module root by locating workflow.py
        workflow_files = list(output_dir.rglob("workflow.py"))
        assert len(workflow_files) == 1, f"Expected exactly one workflow.py, found {workflow_files}"
        generated_root = workflow_files[0].parent

        original_only, generated_only, modified = _compute_diff(
            original_root=original_root,
            generated_root=generated_root,
        )

    # THEN there should be no differences between original and generated files
    assert not original_only and not generated_only and not modified, (
        "Expected zero diff between original and generated workflow files, but found:\n"
        f"original_only={original_only}\n"
        f"generated_only={generated_only}\n"
        f"modified={modified}\n"
    )
