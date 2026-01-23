from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_guardrail_node.workflow import BasicGuardrailNodeWorkflow


def test_serialize_workflow():
    # GIVEN a workflow that uses a guardrail node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicGuardrailNodeWorkflow)

    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 2
    assert not DeepDiff(
        [
            {
                "id": "eb1b1913-9fb8-4b8c-8901-09d9b9edc1c3",
                "key": "actual",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
                "schema": {"type": "string"},
            },
            {
                "id": "545ff95e-e86f-4d06-a991-602781e72605",
                "key": "expected",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
                "schema": {"type": "string"},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables == [{"id": "2abd2b3b-c301-4834-a43f-5db3604f8422", "key": "score", "type": "NUMBER"}]

    # AND its raw data is what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND each node should be serialized correctly
    guardrail_node = next(
        node
        for node in workflow_raw_data["nodes"]
        if node["type"] == "METRIC" and node["data"]["label"] == "Example Guardrail Node"
    )
    assert guardrail_node == {
        "id": "7fef2bbc-cdfc-4f66-80eb-2a52ee52da5f",
        "type": "METRIC",
        "inputs": [
            {
                "id": "dad627f3-d46d-4f12-b3d0-4aa25a5f24b5",
                "key": "expected",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "545ff95e-e86f-4d06-a991-602781e72605"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "42aef2a5-5dcf-41ea-8da4-1eee1f8baf84",
                "key": "actual",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "eb1b1913-9fb8-4b8c-8901-09d9b9edc1c3"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Example Guardrail Node",
            "source_handle_id": "baa8baa7-8849-4b96-a90d-c0545a60d3a8",
            "target_handle_id": "53c299c7-1df2-4d54-bb0d-559a4947c16d",
            "error_output_id": None,
            "metric_definition_id": "example_metric_definition",
            "release_tag": "LATEST",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "module": ["vellum", "workflows", "nodes", "displayable", "guardrail_node", "node"],
            "name": "GuardrailNode",
        },
        "definition": {
            "module": ["tests", "workflows", "basic_guardrail_node", "workflow"],
            "name": "ExampleGuardrailNode",
        },
        "trigger": {
            "id": "53c299c7-1df2-4d54-bb0d-559a4947c16d",
            "merge_behavior": "AWAIT_ANY",
        },
        "ports": [{"id": "baa8baa7-8849-4b96-a90d-c0545a60d3a8", "name": "default", "type": "DEFAULT"}],
    }

    # AND the display data is what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}}

    # AND the definition is what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicGuardrailNodeWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_guardrail_node",
            "workflow",
        ],
    }
