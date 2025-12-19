from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.mocks import MockNodeExecution


def test_mocks__parse_none_still_runs():
    # GIVEN a Base Node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow class with that Node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = StartNode.Outputs.foo

    # AND we parsed `None` on `MockNodeExecution`
    node_output_mocks = MockNodeExecution.validate_all(
        None,
        MyWorkflow,
    )

    # WHEN we run the workflow
    workflow = MyWorkflow()
    final_event = workflow.run(node_output_mocks=node_output_mocks)

    # THEN it was successful
    assert final_event.name == "workflow.execution.fulfilled"
