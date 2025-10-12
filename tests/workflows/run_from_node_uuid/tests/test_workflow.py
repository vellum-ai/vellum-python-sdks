import pytest
from uuid import UUID

from tests.workflows.run_from_node_uuid.workflow import Node2, RunFromNodeUuidWorkflow


def test_run_from_node_with_uuid__happy_path():
    """
    Test that workflows can be resumed from a specific node using UUID.
    """

    workflow = RunFromNodeUuidWorkflow()

    node2_uuid = Node2.__id__
    assert isinstance(node2_uuid, UUID)

    final_event = workflow.run(entrypoint_nodes=[node2_uuid])

    assert final_event.name == "workflow.execution.fulfilled"

    assert final_event.outputs.final_result == "node2_executed"


def test_run_from_node_with_uuid__invalid_uuid():
    """
    Test that providing an invalid UUID raises ValueError.
    """

    workflow = RunFromNodeUuidWorkflow()

    invalid_uuid = UUID("00000000-0000-0000-0000-000000000000")

    with pytest.raises(ValueError, match="No node found with UUID"):
        workflow.run(entrypoint_nodes=[invalid_uuid])


def test_run_from_node_with_sequence__backward_compatibility():
    """
    Test that the original Sequence[Type[BaseNode]] interface still works.
    """

    workflow = RunFromNodeUuidWorkflow()

    final_event = workflow.run(entrypoint_nodes=[Node2])

    assert final_event.name == "workflow.execution.fulfilled"

    assert final_event.outputs.final_result == "node2_executed"
