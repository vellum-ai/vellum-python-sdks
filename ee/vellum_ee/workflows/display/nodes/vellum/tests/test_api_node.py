from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.nodes.displayable.api_node.node import APINode
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_node__api_node_with_timeout():
    # GIVEN an API node with timeout specified
    class MyAPINode(APINode):
        url = "https://api.example.com"
        method = APIRequestMethod.GET
        timeout = 30  # This is the key attribute we're testing

    # AND a workflow with the API node
    class Workflow(BaseWorkflow):
        graph = MyAPINode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the timeout
    my_api_node = next(node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "API")

    # Assert that timeout is present in the serialized attributes
    timeout_attribute = next((attr for attr in my_api_node.get("attributes", []) if attr["name"] == "timeout"), None)

    assert timeout_attribute is not None, "timeout attribute should be present in serialized attributes"
    assert timeout_attribute["value"]["type"] == "CONSTANT_VALUE"
    assert timeout_attribute["value"]["value"]["type"] == "NUMBER"
    assert timeout_attribute["value"]["value"]["value"] == 30.0
