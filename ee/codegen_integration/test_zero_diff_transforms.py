import pytest
import difflib
import importlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Dict, FrozenSet, List, Tuple

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
    ignore_files: FrozenSet[str] = frozenset(),
) -> Tuple[List[str], List[str], Dict[str, str]]:
    """
    Compare files between original and generated directories.

    Args:
        original_root: Path to the original workflow directory.
        generated_root: Path to the generated workflow directory.
        ignore_files: Set of relative file paths to ignore from the diff comparison.

    Returns:
        (original_only, generated_only, modified_diffs) where
        modified_diffs maps relative file path -> unified diff string.
    """
    original_files = _collect_file_map(original_root)
    generated_files = _collect_file_map(generated_root)

    orig_keys = set(original_files.keys()) - ignore_files
    gen_keys = set(generated_files.keys()) - ignore_files

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


@pytest.mark.parametrize(
    "module_name,ignore_files",
    [
        (
            "builtin_list_str",
            frozenset(
                {
                    "__init__.py",
                    "display/nodes/raw_code.py",
                    "display/nodes/the_end.py",
                    "display/workflow.py",
                    "nodes/raw_code/__init__.py",
                    "nodes/the_end.py",
                }
            ),
        ),
        (
            "tool_calling_node_with_custom_run_subworkflow",
            frozenset(
                {
                    "__init__.py",
                    "display/nodes/agent/__init__.py",
                    "display/nodes/agent/transform_text_tool/__init__.py",
                    "display/nodes/agent/transform_text_tool/nodes/transform_node.py",
                    "display/nodes/agent/transform_text_tool/workflow.py",
                    "display/workflow.py",
                    "inputs.py",
                    "nodes/agent/__init__.py",
                    "nodes/agent/transform_text_tool/__init__.py",
                    "nodes/agent/transform_text_tool/inputs.py",
                    "nodes/agent/transform_text_tool/workflow.py",
                    "nodes/agent/transform_text_tool/nodes/__init__.py",
                    "workflow.py",
                }
            ),
        ),
        (
            "trivial",
            frozenset(
                {
                    "__init__.py",
                    "display/nodes/start.py",
                    "display/workflow.py",
                }
            ),
        ),
        (
            "sibling_directory_preservation",
            frozenset(
                {
                    "__init__.py",
                    "display/nodes/start.py",
                    "display/workflow.py",
                }
            ),
        ),
    ],
)
def test_zero_diff_transforms(module_name: str, ignore_files: FrozenSet[str]):
    """
    Tests that serializing a workflow, running codegen with file merging, and comparing
    files produces no diff (excluding files in the ignore list).

    GIVEN a workflow defined in tests.workflows.{module_name}
    WHEN we serialize it to exec_config and run TypeScript codegen with the original
         files as the artifact for file merging
    THEN the generated files match the original workflow files (zero diff), excluding
         any files specified in ignore_files.
    """

    # GIVEN the original workflow module
    workflow_module = f"tests.workflows.{module_name}"

    # Load the workflow submodule to get the actual file path
    # We import the .workflow submodule because the parent package may be a namespace
    # package (no __init__.py) which would have __file__ = None
    workflow_submodule = importlib.import_module(f"{workflow_module}.workflow")
    workflow_file = workflow_submodule.__file__
    assert workflow_file is not None, f"Module {workflow_module}.workflow has no __file__"
    original_root = Path(workflow_file).parent

    # Collect original files for diff comparison later
    original_files = _collect_file_map(original_root)

    # WHEN we serialize the workflow to exec_config
    serialization_result = BaseWorkflowDisplay.serialize_module(workflow_module)
    original_exec_config = serialization_result.exec_config

    # AND we run codegen on the serialized data with the original artifact directory
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
                "--original-artifact",
                str(original_root),
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
            ignore_files=ignore_files,
        )

        modified_paths = sorted(modified_diffs.keys())

        # Collect file contents for showing full diffs of added/removed files
        generated_files = _collect_file_map(generated_root)

        # Build diff text with added/removed files shown in diff syntax
        diff_parts = []

        # Show removed files (files in original but not in generated) with full content
        for rel in original_only:
            original_content = original_files[rel].splitlines()
            diff_lines = difflib.unified_diff(
                original_content,
                [],
                fromfile=f"a/{rel}",
                tofile="/dev/null",
                lineterm="",
            )
            diff_parts.append("\n".join(diff_lines))

        # Show added files (files in generated but not in original) with full content
        for rel in generated_only:
            generated_content = generated_files[rel].splitlines()
            diff_lines = difflib.unified_diff(
                [],
                generated_content,
                fromfile="/dev/null",
                tofile=f"b/{rel}",
                lineterm="",
            )
            diff_parts.append("\n".join(diff_lines))

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
