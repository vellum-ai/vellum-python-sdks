import json
import os
import tempfile
from unittest.mock import patch

from vellum_ee.workflows.display.utils.metadata import load_edges_to_id_mapping


def test_load_edges_to_id_mapping__normalizes_relative_paths():
    """
    Tests that load_edges_to_id_mapping normalizes relative paths to absolute paths.
    """

    # GIVEN metadata.json with relative paths (legacy format)
    scheduled_edge_id = "8826b88e-95c9-4fe2-8000-b00c22db084c"
    manual_edge_id = "e45d4434-b73c-462f-987a-8933452d285b"
    metadata_content = {
        "edges_to_id_mapping": {
            ".triggers.scheduled.Scheduled|.nodes.output.Output.Trigger": scheduled_edge_id,
            "vellum.workflows.triggers.manual.Manual|.nodes.output.Output.Trigger": manual_edge_id,
        }
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        # AND a workflow module structure
        workflow_root = "my_workflow"
        workflow_dir = os.path.join(tmpdir, workflow_root)
        os.makedirs(workflow_dir)

        metadata_path = os.path.join(workflow_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata_content, f)

        def mock_virtual_open(path):
            return open(metadata_path)

        with patch(
            "vellum_ee.workflows.display.utils.metadata.find_workflow_root_with_metadata",
            return_value=workflow_root,
        ):
            with patch(
                "vellum_ee.workflows.display.utils.metadata.virtual_open",
                side_effect=mock_virtual_open,
            ):
                # WHEN we load the edges mapping
                result = load_edges_to_id_mapping(workflow_root)

                # THEN relative paths are normalized to absolute paths
                scheduled_source = f"{workflow_root}.triggers.scheduled.Scheduled"
                scheduled_target = f"{workflow_root}.nodes.output.Output.Trigger"
                expected_scheduled_key = f"{scheduled_source}|{scheduled_target}"
                assert expected_scheduled_key in result
                assert result[expected_scheduled_key] == scheduled_edge_id

                # AND the manual trigger path (already absolute) is preserved with normalized target
                manual_source = "vellum.workflows.triggers.manual.Manual"
                manual_target = f"{workflow_root}.nodes.output.Output.Trigger"
                expected_manual_key = f"{manual_source}|{manual_target}"
                assert expected_manual_key in result
                assert result[expected_manual_key] == manual_edge_id


def test_load_edges_to_id_mapping__preserves_absolute_paths():
    """
    Tests that load_edges_to_id_mapping preserves already-absolute paths.
    """

    # GIVEN metadata.json with absolute paths (new format)
    scheduled_edge_id = "8826b88e-95c9-4fe2-8000-b00c22db084c"
    manual_edge_id = "e45d4434-b73c-462f-987a-8933452d285b"
    scheduled_key = "my_workflow.triggers.scheduled.Scheduled|my_workflow.nodes.output.Output.Trigger"
    manual_key = "vellum.workflows.triggers.manual.Manual|my_workflow.nodes.output.Output.Trigger"
    metadata_content = {
        "edges_to_id_mapping": {
            scheduled_key: scheduled_edge_id,
            manual_key: manual_edge_id,
        }
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        # AND a workflow module structure
        workflow_root = "my_workflow"
        workflow_dir = os.path.join(tmpdir, workflow_root)
        os.makedirs(workflow_dir)

        metadata_path = os.path.join(workflow_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata_content, f)

        def mock_virtual_open(path):
            return open(metadata_path)

        with patch(
            "vellum_ee.workflows.display.utils.metadata.find_workflow_root_with_metadata",
            return_value=workflow_root,
        ):
            with patch(
                "vellum_ee.workflows.display.utils.metadata.virtual_open",
                side_effect=mock_virtual_open,
            ):
                # WHEN we load the edges mapping
                result = load_edges_to_id_mapping(workflow_root)

                # THEN absolute paths are preserved unchanged
                assert scheduled_key in result
                assert result[scheduled_key] == scheduled_edge_id

                # AND the manual trigger path is preserved
                assert manual_key in result
                assert result[manual_key] == manual_edge_id
