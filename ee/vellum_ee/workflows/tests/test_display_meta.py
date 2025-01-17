import pytest
import os
import sys
from uuid import UUID, uuid4

from vellum.workflows import BaseWorkflow
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


@pytest.fixture
def files() -> dict[str, str]:
    base_directory = os.path.join(os.path.dirname(__file__), "local_workflow")
    files = {}

    for root, _, filenames in os.walk(base_directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            # Key will be the relative path inside `local_files`
            relative_path = str(os.path.relpath(file_path, start=base_directory))
            with open(file_path, encoding="utf-8") as f:
                files[relative_path] = f.read()

    return files


def test_base_class_dynamic_import(files):
    namespace = str(uuid4())  # Create a unique namespace
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    Workflow = BaseWorkflow.load_from_module(namespace)
    WorkflowDisplay = BaseWorkflow.get_workflow_display(namespace)
    display_meta = BaseWorkflow.gather_display_meta(WorkflowDisplay, Workflow) if WorkflowDisplay else {}

    expected_result = {
        "global_node_output_displays": {
            "result": {"id": UUID("423bc529-1a1a-4f72-af4d-cbdb5f0a5929"), "name": "result"},
            "value": {"id": UUID("5469b810-6ea6-4362-9e79-e360d44a1405"), "name": "value"},
        },
        "global_workflow_input_displays": {
            "input_value": {
                "color": None,
                "id": UUID("2268a996-bd17-4832-b3ff-f5662d54b306"),
                "name": "input-value",
                "required": True,
            }
        },
        "node_displays": {
            UUID("533c6bd8-6088-4abc-a168-8c1758abcd33"): {
                "result": {"id": UUID("423bc529-1a1a-4f72-af4d-cbdb5f0a5929"), "name": "result"}
            },
            UUID("f3ef4b2b-fec9-4026-9cc6-e5eac295307f"): {
                "value": {"id": UUID("5469b810-6ea6-4362-9e79-e360d44a1405"), "name": "value"}
            },
        },
        "workflow_inputs": {
            "input_value": {
                "color": None,
                "id": UUID("2268a996-bd17-4832-b3ff-f5662d54b306"),
                "name": "input-value",
                "required": True,
            }
        },
        "workflow_outputs": {
            "final_output": {
                "edge_id": UUID("417c56a4-cdc1-4f9d-a10c-b535163f51e8"),
                "id": UUID("5469b810-6ea6-4362-9e79-e360d44a1405"),
                "label": "Final Output",
                "name": "final-output",
                "node_id": UUID("f3ef4b2b-fec9-4026-9cc6-e5eac295307f"),
                "node_input_id": UUID("fe6cba85-2423-4b5e-8f85-06311a8be5fb"),
                "target_handle_id": UUID("3ec34f6e-da48-40d5-a65b-a48fefa75763"),
            }
        },
    }
    assert display_meta == expected_result
