import json
from typing import Any, Dict

from deepdiff import DeepDiff

from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_code_to_display_data(code_to_display_fixture_paths):
    """Confirms that code representations of workflows are correctly serialized into their display representations."""

    expected_display_data_file_path, code_dir = code_to_display_fixture_paths
    base_module_path = __name__.split(".")[:-1]
    code_sub_path = code_dir.split("/".join(base_module_path))[1].split("/")[1:]
    module_path = ".".join(base_module_path + code_sub_path)

    workflow = BaseWorkflow.load_from_module(module_path)
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=workflow)
    actual_serialized_workflow: dict = workflow_display.serialize()

    with open(expected_display_data_file_path) as file:
        expected_serialized_workflow = json.load(file, object_hook=_custom_obj_hook)  # noqa: F841


    assert not DeepDiff(
        expected_serialized_workflow,
        actual_serialized_workflow,
        significant_digits=6,
        # This is for the input_variables order being out of order sometimes.
        ignore_order=True
    )


def _process_position_hook(key, value) -> None:
    """
    Private hook to ensure 'position' keys 'x' and 'y' are floats instead of ints.
    x and y in json is int so json library parses to int even though we have it as float in our serializers
    """
    if key == 'position' and isinstance(value, dict):
        if 'x' in value and isinstance(value['x'], int):
            value['x'] = float(value['x'])
        if 'y' in value and isinstance(value['y'], int):
            value['y'] = float(value['y'])

def _process_negated_hook(key, value, current_json_obj) -> None:
    """
    Private hook to replace the 'negated' key's None value with False.
    negated can be sent as null in the raw payload, but we expect serialization to produce boolean values
    """
    if key == 'negated' and value is None:
        current_json_obj[key] = False

def _custom_obj_hook(json_dict) -> Dict[str, Any]:
    """
    Private hook to convert some raw json items to values we expect.
    """
    for key, value in list(json_dict.items()):
        _process_position_hook(key,value)
        _process_negated_hook(key, value, json_dict)
    return json_dict
