import pytest
import json
from pathlib import Path
import subprocess
import tempfile

from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


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
    Tests that serializing a workflow, running codegen, and re-serializing produces no diff.
    """

    # GIVEN a workflow module
    workflow_module = f"tests.workflows.{module_name}"

    # WHEN we serialize the workflow
    serialization_result = BaseWorkflowDisplay.serialize_module(workflow_module)
    original_exec_config = serialization_result.exec_config

    # AND we run codegen on the serialized data
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the exec config to a temp file for codegen
        exec_config_path = Path(temp_dir) / "exec_config.json"
        exec_config_path.write_text(json.dumps(original_exec_config))

        # Run codegen via npm/tsx
        codegen_dir = Path(__file__).parent.parent / "codegen"
        output_dir = Path(temp_dir) / "generated"
        output_dir.mkdir()

        # Invoke the TypeScript codegen
        result = subprocess.run(
            [
                "npx",
                "tsx",
                str(codegen_dir / "src" / "project.ts"),
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
        )

        if result.returncode != 0:
            pytest.fail(f"Codegen failed: {result.stderr}")

        # Re-serialize the generated code
        # Add the generated directory to sys.path so we can import it
        import sys

        sys.path.insert(0, str(output_dir))
        try:
            regenerated_module = f"{module_name}"
            regenerated_result = BaseWorkflowDisplay.serialize_module(regenerated_module)
            regenerated_exec_config = regenerated_result.exec_config
        finally:
            sys.path.remove(str(output_dir))

    # THEN the two serializations should be identical (no diff)
    assert original_exec_config == regenerated_exec_config, (
        "Expected no diff between original and regenerated workflow, "
        f"but found differences:\n{json.dumps(original_exec_config, indent=2)}\n"
        f"vs\n{json.dumps(regenerated_exec_config, indent=2)}"
    )
