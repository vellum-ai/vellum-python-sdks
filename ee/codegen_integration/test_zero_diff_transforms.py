import pytest
import difflib
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
) -> Tuple[List[str], List[str], Dict[str, str]]:
    """
    Compare files between original and generated directories.

    Returns:
        (original_only, generated_only, modified_diffs) where
        modified_diffs maps relative file path -> unified diff string.
    """
    original_files = _collect_file_map(original_root)
    generated_files = _collect_file_map(generated_root)

    orig_keys = set(original_files.keys())
    gen_keys = set(generated_files.keys())

    original_only = sorted(orig_keys - gen_keys)
    generated_only = sorted(gen_keys - orig_keys)

    modified_diffs: Dict[str, str] = {}

    for rel in sorted(orig_keys & gen_keys):
        original_content = original_files[rel]
        generated_content = generated_files[rel]
        if original_content == generated_content:
            continue

        diff_lines = difflib.unified_diff(
            original_content.splitlines(),
            generated_content.splitlines(),
            fromfile=f"original/{rel}",
            tofile=f"generated/{rel}",
            lineterm="",
        )
        modified_diffs[rel] = "\n".join(diff_lines)

    return original_only, generated_only, modified_diffs


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

        generated_root = output_dir / module_name

        original_only, generated_only, modified_diffs = _compute_diff(
            original_root=original_root,
            generated_root=generated_root,
        )

        modified_paths = sorted(modified_diffs.keys())

        # Build diff text with added/removed files shown in diff syntax
        diff_parts = []

        # Show removed files (files in original but not in generated)
        for rel in original_only:
            diff_parts.append(f"--- a/{rel}\n+++ /dev/null\n@@ File removed @@")

        # Show added files (files in generated but not in original)
        for rel in generated_only:
            diff_parts.append(f"--- /dev/null\n+++ b/{rel}\n@@ File added @@")

        # Show modified files
        for rel in modified_paths:
            diff_parts.append(f"Diff for {rel}:\n{modified_diffs[rel]}")

        diff_text = "\n\n".join(diff_parts) if diff_parts else ""

        if result.stdout:
            diff_text += f"\nCodegen output:\n{result.stdout}"

    # THEN there should be no differences between original and generated files
    assert not original_only and not generated_only and not modified_paths, (
        f"Expected zero diff for test workflow '{module_name}' between original and generated files, but found:\n"
        f"original_only={original_only}\n"
        f"generated_only={generated_only}\n"
        f"modified={modified_paths}\n"
        f"{diff_text}\n"
    )
