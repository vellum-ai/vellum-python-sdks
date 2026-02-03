import pytest
import json
from typing import Any, Dict, List

from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


@pytest.mark.usefixtures("workspace_secret_client", "deployment_client")
def test_code_to_display_data(code_to_display_fixture_paths, mock_trigger_metadata):
    """Confirms that code representations of workflows are correctly serialized into their display representations."""

    expected_display_data_file_path, code_dir = code_to_display_fixture_paths
    base_module_path = __name__.split(".")[:-1]
    code_sub_path = code_dir.split("/".join(base_module_path))[1].split("/")[1:]
    module_path = ".".join(base_module_path + code_sub_path)

    actual_serialized_workflow: dict = BaseWorkflowDisplay.serialize_module(module_path).exec_config

    with open(expected_display_data_file_path) as file:
        expected_serialized_workflow = json.load(file, object_hook=_custom_obj_hook)  # noqa: F841

    _copy_schema_fields(expected_serialized_workflow, actual_serialized_workflow)

    diff = DeepDiff(
        expected_serialized_workflow,
        actual_serialized_workflow,
        significant_digits=6,
        # This is for the input_variables order being out of order sometimes.
        ignore_order=True,
        exclude_regex_paths=[
            r"root\['workflow_raw_data'\]\['edges'\]\[\d+\]\['target_handle_id'\]",
            # This is for output values since this currently isn't serialized yet
            r"root\['workflow_raw_data'\]\['nodes'\]\[\d+\]\['data'\]\['workflow_raw_data'\]\['output_values'\]",
        ],
    )
    assert not diff


def _copy_schema_fields(expected: Dict[str, Any], actual: Dict[str, Any]) -> None:
    """
    Copies schema fields from actual serialized workflow to expected.
    This allows fixtures to not include schema values while still comparing the rest of the structure.
    """

    def process_nodes(expected_nodes: List[Dict[str, Any]], actual_nodes: List[Dict[str, Any]]) -> None:
        actual_nodes_by_id = {node["id"]: node for node in actual_nodes}
        for expected_node in expected_nodes:
            actual_node = actual_nodes_by_id.get(expected_node["id"])
            if not actual_node:
                continue

            actual_attrs_by_name = {attr.get("name"): attr for attr in actual_node.get("attributes", [])}
            for expected_attr in expected_node.get("attributes", []):
                actual_attr = actual_attrs_by_name.get(expected_attr.get("name"))
                if actual_attr and "schema" in actual_attr:
                    expected_attr["schema"] = actual_attr["schema"]

            if "data" in expected_node and "workflow_raw_data" in expected_node.get("data", {}):
                nested_expected = expected_node["data"]["workflow_raw_data"].get("nodes", [])
                nested_actual = actual_node.get("data", {}).get("workflow_raw_data", {}).get("nodes", [])
                if nested_expected and nested_actual:
                    process_nodes(nested_expected, nested_actual)

    expected_nodes = expected.get("workflow_raw_data", {}).get("nodes", [])
    actual_nodes = actual.get("workflow_raw_data", {}).get("nodes", [])
    process_nodes(expected_nodes, actual_nodes)


def _process_position_hook(key, value) -> None:
    """
    Private hook to ensure 'position' keys 'x' and 'y' are floats instead of ints.
    x and y in json is int so json library parses to int even though we have it as float in our serializers
    """
    if key == "position" and isinstance(value, dict):
        if "x" in value and isinstance(value["x"], int):
            value["x"] = float(value["x"])
        if "y" in value and isinstance(value["y"], int):
            value["y"] = float(value["y"])


def _process_negated_hook(key, value, current_json_obj) -> None:
    """
    Private hook to replace the 'negated' key's None value with False.
    negated can be sent as null in the raw payload, but we expect serialization to produce boolean values
    """
    if key == "negated" and value is None:
        current_json_obj[key] = False


def _process_display_data_none_fields_hook(key, value, current_json_obj) -> None:
    """
    Private hook to remove display_data fields with None values.
    Fields like z_index, width, height can be null in raw JSON, but we don't include them
    in generated Python code when they're None (to keep generated code clean).
    """
    if key == "display_data" and isinstance(value, dict):
        # Remove None values for optional display fields
        for field in ["z_index", "width", "height"]:
            if field in value and value[field] is None:
                del value[field]


def _custom_obj_hook(json_dict) -> Dict[str, Any]:
    """
    Private hook to convert some raw json items to values we expect.
    """
    for key, value in list(json_dict.items()):
        _process_position_hook(key, value)
        _process_negated_hook(key, value, json_dict)
        _process_display_data_none_fields_hook(key, value, json_dict)
    return json_dict
