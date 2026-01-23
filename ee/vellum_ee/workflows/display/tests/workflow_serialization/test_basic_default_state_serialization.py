from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_default_state.workflow import BasicDefaultStateWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that has a simple state definition
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicDefaultStateWorkflow)

    serialized_workflow: dict = workflow_display.serialize()
    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1
    assert not DeepDiff(
        [
            {
                "id": "0bbe085c-31d3-4b48-b74d-d501f592da90",
                "key": "example",
                "type": "STRING",
                "default": {"type": "STRING", "value": "hello"},
                "required": False,
                "extensions": {"color": None},
                "schema": {"type": "string"},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its state variables should be what we expect
    state_variables = serialized_workflow["state_variables"]
    assert len(state_variables) == 1
    assert not DeepDiff(
        [
            {
                "id": "829a8335-d425-414e-9c0b-62e820156df5",
                "key": "example",
                "type": "NUMBER",
                "default": {"type": "NUMBER", "value": 5.0},
                "required": False,
                "extensions": {"color": None},
            },
        ],
        state_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {
                "id": "6e7eeaa5-9559-4ae3-8606-e52ead5805a5",
                "key": "example_input",
                "type": "STRING",
            },
            {
                "id": "e3ae0fe3-7590-4eac-b808-45901d82f2ba",
                "key": "example_state",
                "type": "NUMBER",
            },
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "32684932-7c7c-4b1c-aed2-553de29bf3f7",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "e4136ee4-a51a-4ca3-9a3a-aa96f5de2347",
        },
        "base": None,
        "definition": None,
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
        },
    }

    # AND the display data should be what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {
        "viewport": {
            "x": 0.0,
            "y": 0.0,
            "zoom": 1.0,
        }
    }

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicDefaultStateWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_default_state",
            "workflow",
        ],
    }
