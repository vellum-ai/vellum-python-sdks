import pytest

from tests.workflows.streaming_node_pipeline.workflow import Inputs, StreamingNodePipelineWorkflow


# We're using a threading Event to coordinate work between nodes.
# Add a timeout to guard against deadlocks.
@pytest.mark.timeout(5)
def test_workflow__happy_path():
    """
    Ensure that we can successfully pipeline the outputs from one streaming node to the next.
    """

    # GIVEN a workflow with two pipelined streaming nodes
    workflow = StreamingNodePipelineWorkflow()

    # WHEN we run the workflow
    final_event = workflow.run(inputs=Inputs(fruits=["apple", "banana", "cherry"]))

    # THEN we get the expected outputs
    assert final_event.name == "workflow.execution.fulfilled"
    assert final_event.outputs.final_state == [
        "elppa",
        "elppa elppa",
        "ananab",
        "ananab ananab",
        "yrrehc",
        "yrrehc yrrehc",
    ]
    assert final_event.outputs.final_value == ["elppa elppa", "ananab ananab", "yrrehc yrrehc"]
