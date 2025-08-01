import pytest
import os
import sys
from uuid import uuid4

from vellum.workflows import BaseWorkflow
from vellum.workflows.events.workflow import WorkflowEventDisplayContext
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay
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
    display_meta = BaseWorkflowDisplay.gather_event_display_context(namespace, Workflow)

    expected_result = {
        "node_displays": {
            "533c6bd8-6088-4abc-a168-8c1758abcd33": {
                "input_display": {
                    "example_var_1": "a0d1d7cf-242a-4bd9-a437-d308a7ced9b3",
                    "template": "f97d721a-e685-498e-90c3-9c3d9358fdad",
                },
                "output_display": {"result": "423bc529-1a1a-4f72-af4d-cbdb5f0a5929"},
                "port_display": {"default": "afda9a19-0618-42e1-9b63-5d0db2a88f62"},
                "subworkflow_display": None,
            },
            "f3ef4b2b-fec9-4026-9cc6-e5eac295307f": {
                "input_display": {"node_input": "fe6cba85-2423-4b5e-8f85-06311a8be5fb"},
                "output_display": {"value": "5469b810-6ea6-4362-9e79-e360d44a1405"},
                "port_display": {},
                "subworkflow_display": None,
            },
        },
        "workflow_inputs": {"input_value": "2268a996-bd17-4832-b3ff-f5662d54b306"},
        "workflow_outputs": {"final_output": "5469b810-6ea6-4362-9e79-e360d44a1405"},
    }
    assert display_meta
    assert display_meta.model_dump(mode="json") == expected_result


def test_gather_event_display_context__custom_workflow_name():
    # GIVEN a workflow module with a custom workflow name
    workflow_output_id = uuid4()
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow

class MyCustomWorkflow(BaseWorkflow):
    class Outputs(BaseWorkflow.Outputs):
        answer = "foo"
""",
        "display/__init__.py": """\
# flake8: noqa: F401, F403

from .workflow import *
""",
        "display/workflow.py": f"""\
from uuid import UUID
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay
from vellum_ee.workflows.display.base import WorkflowOutputDisplay
from ..workflow import MyCustomWorkflow

class MyCustomWorkflowDisplay(BaseWorkflowDisplay[MyCustomWorkflow]):
    output_displays = {{
        MyCustomWorkflow.Outputs.answer: WorkflowOutputDisplay(
            id=UUID("{workflow_output_id}"), name="answer"
        )
    }}
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # WHEN the workflow display context is gathered
    Workflow = BaseWorkflow.load_from_module(namespace)
    display_meta = BaseWorkflowDisplay.gather_event_display_context(namespace, Workflow)

    # THEN the workflow display context is successfully gathered
    assert display_meta
    assert display_meta.workflow_outputs == {
        "answer": workflow_output_id,
    }


def test_gather_event_display_context__workflow_crawling_without_display_module():
    # GIVEN a workflow module without a display module
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode

class TestNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

class TestWorkflow(BaseWorkflow):
    graph = TestNode
    
    class Outputs(BaseWorkflow.Outputs):
        final_result = TestNode.Outputs.result
""",
    }

    namespace = str(uuid4())

    # AND the virtual file loader is registered
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    # WHEN the workflow display context is gathered
    display_meta = BaseWorkflowDisplay.gather_event_display_context(namespace)

    # THEN the workflow display context should be successfully created via workflow crawling
    assert display_meta is not None
    assert isinstance(display_meta, WorkflowEventDisplayContext)

    # AND the node displays should be populated with the correct node structure
    assert len(display_meta.node_displays) == 1
    node_display = list(display_meta.node_displays.values())[0]
    assert "result" in node_display.output_display

    assert "final_result" in display_meta.workflow_outputs
