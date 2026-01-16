from deepdiff import DeepDiff

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_map_node.workflow import SimpleMapExample


def test_serialize_workflow():
    # GIVEN a Workflow that uses a MapNode
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=SimpleMapExample)
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
                "id": "db2eb237-38e4-417a-8bfc-5bda0f3165ca",
                "key": "fruits",
                "type": "JSON",
                "required": True,
                "default": None,
                "extensions": {"color": None},
                "schema": {"type": "array", "items": {"type": "string"}},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert not DeepDiff(
        [
            {
                "id": "145b0b68-224b-4f83-90e6-eea3457e6c3e",
                "key": "final_value",
                "type": "JSON",
            },
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND each node should be serialized correctly

    map_node = next(n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "MapNode")

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "SimpleMapExample",
        "module": [
            "tests",
            "workflows",
            "basic_map_node",
            "workflow",
        ],
    }

    # AND the map node's items input ID should match the subworkflow's items input ID
    items_input_id = map_node["data"]["items_input_id"]
    assert map_node["inputs"][0]["id"] == items_input_id


def test_serialize_workflow__dynamic_field_reference_items():
    """Tests that a map node with items set to a dynamic field reference serializes correctly."""

    # GIVEN a prompt node with json output
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []

    # AND a simple subworkflow for the map node
    class IterationNode(BaseNode):
        item = MapNode.SubworkflowInputs.item

        class Outputs(BaseOutputs):
            value: str

        def run(self) -> Outputs:
            return self.Outputs(value=str(self.item))

    class IterationSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = IterationNode

        class Outputs(BaseOutputs):
            value = IterationNode.Outputs.value

    # AND a map node with items set to a dynamic field reference
    class DynamicItemsMapNode(MapNode):
        items = MyPromptNode.Outputs.json["items"]
        subworkflow = IterationSubworkflow

    # AND a workflow using these nodes
    class DynamicFieldReferenceWorkflow(BaseWorkflow):
        graph = MyPromptNode >> DynamicItemsMapNode

        class Outputs(BaseOutputs):
            result = DynamicItemsMapNode.Outputs.value

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=DynamicFieldReferenceWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the map node should be serialized
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    map_node = next(n for n in workflow_raw_data["nodes"] if n.get("type") == "MAP")

    # AND the attributes should contain the items with a BINARY_EXPRESSION
    attributes = map_node["attributes"]
    items_attribute = next(attr for attr in attributes if attr["name"] == "items")
    items_value = items_attribute["value"]
    assert items_value["type"] == "BINARY_EXPRESSION"
    assert items_value["operator"] == "accessField"
    assert items_value["rhs"]["type"] == "CONSTANT_VALUE"
    assert items_value["rhs"]["value"]["value"] == "items"
