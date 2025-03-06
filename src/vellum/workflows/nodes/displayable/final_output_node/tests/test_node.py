import pytest

from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.state.base import BaseState


def test_final_output_node__mismatched_output_type():
    # GIVEN a FinalOutputNode with a mismatched output type
    class StringOutputNode(FinalOutputNode[BaseState, str]):
        class Outputs(FinalOutputNode.Outputs):
            value = {"foo": "bar"}

    # WHEN the node is run
    node = StringOutputNode()
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN an error is raised
    assert str(exc_info.value) == "Expected an output of type 'str', but received 'dict'"
