from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.note_node.node import NoteNode
from vellum_ee.workflows.display.nodes.vellum.note_node import BaseNoteNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_node__note_node():
    # GIVEN a note node
    class MyNoteNode(NoteNode):
        pass

    # AND a display class for the note node
    class MyNoteNodeDisplay(BaseNoteNodeDisplay[MyNoteNode]):
        text = "This makes sense"
        style = {
            "fontSize": 24,
        }

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyNoteNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_note_node = next(node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "NOTE")

    assert my_note_node["inputs"] == []
    assert my_note_node["data"]["text"] == "This makes sense"
    assert my_note_node["data"]["style"] == {"fontSize": 24}
