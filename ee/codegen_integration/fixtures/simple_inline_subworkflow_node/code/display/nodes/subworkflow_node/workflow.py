from uuid import UUID

from vellum_ee.workflows.display.vellum import (
    EdgeVellumDisplayOverrides,
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    NodeDisplayPosition,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowMetaVellumDisplayOverrides,
    WorkflowOutputVellumDisplayOverrides,
)
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay

from ....nodes.subworkflow_node.nodes.final_output import FinalOutput
from ....nodes.subworkflow_node.nodes.search_node import SearchNode
from ....nodes.subworkflow_node.workflow import SubworkflowNodeWorkflow


class SubworkflowNodeWorkflowDisplay(VellumWorkflowDisplay[SubworkflowNodeWorkflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("c48f318d-4d87-44da-be54-0ecf537608f6"),
        entrypoint_node_source_handle_id=UUID("cfec8bf4-d335-4681-a5c6-cbd53ffbd0d1"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1196.2209238684252, y=58.34576651524276, zoom=0.8182365497236056)
        ),
    )
    inputs_display = {}
    entrypoint_displays = {
        SearchNode: EntrypointVellumDisplayOverrides(
            id=UUID("c48f318d-4d87-44da-be54-0ecf537608f6"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("96f14f30-7984-4bbf-af02-baf07ce38116")),
        )
    }
    edge_displays = {
        (SearchNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("39582ae7-0a7b-4063-8d67-0e2e8ad45a1e")
        )
    }
    output_displays = {
        SubworkflowNodeWorkflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("6ab3665f-881d-488b-9124-a6da40136c68"),
            node_id=UUID("f3fe1e6e-5a4a-42d8-9cfe-9ecbcb935f72"),
            node_input_id=UUID("8e8c6182-4898-47de-be8f-769edad990ed"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("20aa0107-742b-4662-941f-4f146b3c5565"),
            display_data=NodeDisplayData(
                position=NodeDisplayPosition(x=2750, y=208.7778595317725), width=456, height=233
            ),
            edge_id=UUID("39582ae7-0a7b-4063-8d67-0e2e8ad45a1e"),
        )
    }
