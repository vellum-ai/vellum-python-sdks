from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.note_node.node import NoteNode
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_node__note_node():
    """
    Tests that a single note node is properly serialized in a workflow.
    """

    # GIVEN a note node with text and style defined on the node class
    class MyNoteNode(NoteNode):
        text = "This makes sense"
        style = {
            "fontSize": 24,
        }

    # AND a workflow with the note node
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


def test_serialize_workflow__graph_with_only_note_nodes():
    """
    Tests that a workflow with only note nodes properly serializes all note nodes in the final payload.
    """

    # GIVEN multiple note nodes with text and style defined on the node classes
    class FirstNoteNode(NoteNode):
        text = "First note"
        style = {"fontSize": 16}

    class SecondNoteNode(NoteNode):
        text = "Second note"
        style = {"fontSize": 20}

    # AND a workflow with only note nodes in unused_graphs
    class Workflow(BaseWorkflow):
        unused_graphs = {FirstNoteNode, SecondNoteNode}  # type: ignore[assignment]

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the serialized workflow should contain both note nodes
    note_nodes = [node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "NOTE"]
    assert len(note_nodes) == 2

    # AND the note nodes should have the correct data
    note_texts = {node["data"]["text"] for node in note_nodes}
    assert note_texts == {"First note", "Second note"}

    # AND each note node should have the correct style
    first_note = next(node for node in note_nodes if node["data"]["text"] == "First note")
    second_note = next(node for node in note_nodes if node["data"]["text"] == "Second note")

    assert first_note["data"]["style"] == {"fontSize": 16}
    assert second_note["data"]["style"] == {"fontSize": 20}
