from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


def test_try_node_display__serialize_with_error_output() -> None:
    # GIVEN a Base Node wrapped with a TryNode
    @TryNode.wrap()
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            hello = "world"

    # AND a displayable node referencing
    class OtherNode(TemplatingNode):
        template = "{{ hello }} {{ error }}"
        inputs = {
            "hello": MyNode.Outputs.hello,
            "error": MyNode.Outputs.error,
        }

    # AND a workflow referencing the two nodes
    class MyWorkflow(BaseWorkflow):
        graph = MyNode >> OtherNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=MyWorkflow)
    serialized_workflow = workflow_display.serialize()

    # THEN the correct inputs should be serialized on the node
    serialized_node = next(node for node in serialized_workflow["nodes"] if node["id"] == str(OtherNode.__id__))
    hello_input_value = next(input["value"] for input in serialized_node["data"]["inputs"] if input["name"] == "hello")
    error_input_value = next(input["value"] for input in serialized_node["data"]["inputs"] if input["name"] == "error")
    assert hello_input_value == {"type": "node_output", "node_id": "my_node", "output_name": "hello"}
    assert error_input_value == {"type": "node_output", "node_id": "my_node", "output_name": "error"}
