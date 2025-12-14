from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.note_node.node import NoteNode
from vellum_ee.workflows.display.nodes.vellum.note_node import BaseNoteNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_node__note_node():
    """
    Tests that a single note node is properly serialized in a workflow.
    """

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


def test_serialize_workflow__graph_with_only_note_nodes():
    """
    Tests that a workflow with only note nodes properly serializes all note nodes in the final payload.
    """

    # GIVEN multiple note nodes
    class FirstNoteNode(NoteNode):
        pass

    class SecondNoteNode(NoteNode):
        pass

    # AND display classes for the note nodes
    class FirstNoteNodeDisplay(BaseNoteNodeDisplay[FirstNoteNode]):
        text = "First note"
        style = {"fontSize": 16}

    class SecondNoteNodeDisplay(BaseNoteNodeDisplay[SecondNoteNode]):
        text = "Second note"
        style = {"fontSize": 20}

    # AND a workflow with only note nodes in the graph
    class Workflow(BaseWorkflow):
        graph = {FirstNoteNode, SecondNoteNode}  # type: ignore[assignment]

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
