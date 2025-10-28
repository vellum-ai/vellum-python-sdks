from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode, InlineSubworkflowNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum.workflows.workflows.event_filters import workflow_sandbox_event_filter


class NestedInputs(BaseInputs):
    value: str


class NestedNode(BaseNode):
    value = NestedInputs.value

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"nested: {self.value}")


class NestedWorkflow(BaseWorkflow[NestedInputs, BaseState]):
    graph = NestedNode

    class Outputs(BaseOutputs):
        result = NestedNode.Outputs.result


class ParentInputs(BaseInputs):
    value: str


class SubworkflowNode(InlineSubworkflowNode):
    subworkflow_inputs = {
        "value": ParentInputs.value,
    }
    subworkflow = NestedWorkflow


class ParentWorkflow(BaseWorkflow[ParentInputs, BaseState]):
    graph = SubworkflowNode

    class Outputs(BaseOutputs):
        result = SubworkflowNode.Outputs.result


def test_workflow_sandbox_event_filter__filters_nested_workflow_snapshotted_events():
    """
    Tests that workflow_sandbox_event_filter filters out snapshotted events from nested workflows.
    """

    workflow = ParentWorkflow()

    # WHEN we stream the workflow with workflow_sandbox_event_filter
    events = list(
        workflow.stream(
            inputs=ParentInputs(value="test"),
            event_filter=workflow_sandbox_event_filter,
        )
    )

    snapshotted_events = [e for e in events if e.name == "workflow.execution.snapshotted"]
    assert len(snapshotted_events) > 0

    for event in snapshotted_events:
        assert event.workflow_definition == ParentWorkflow


def test_workflow_sandbox_event_filter__includes_root_workflow_snapshotted_events():
    """
    Tests that workflow_sandbox_event_filter includes snapshotted events from the root workflow.
    """

    class SimpleNode(BaseNode):
        class Outputs(BaseOutputs):
            result: str = "simple"

        def run(self) -> Outputs:
            return self.Outputs()

    class SimpleWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = SimpleNode

        class Outputs(BaseOutputs):
            result = SimpleNode.Outputs.result

    workflow = SimpleWorkflow()

    # WHEN we stream the workflow with workflow_sandbox_event_filter
    events = list(
        workflow.stream(
            inputs=BaseInputs(),
            event_filter=workflow_sandbox_event_filter,
        )
    )

    snapshotted_events = [e for e in events if e.name == "workflow.execution.snapshotted"]
    assert len(snapshotted_events) > 0

    for event in snapshotted_events:
        assert event.workflow_definition == SimpleWorkflow
