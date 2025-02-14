from uuid import UUID

from vellum_ee.workflows.display.base import WorkflowOutputDisplay
from vellum_ee.workflows.display.vellum import (
    EdgeVellumDisplayOverrides,
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    NodeDisplayPosition,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsVellumDisplayOverrides,
    WorkflowMetaVellumDisplayOverrides,
)
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay

from ....nodes.map_node.inputs import Inputs
from ....nodes.map_node.nodes.final_output import FinalOutput
from ....nodes.map_node.nodes.search_node import SearchNode
from ....nodes.map_node.nodes.templating_node import TemplatingNode
from ....nodes.map_node.workflow import MapNodeWorkflow


class MapNodeWorkflowDisplay(VellumWorkflowDisplay[MapNodeWorkflow]):
    workflow_display = WorkflowMetaVellumDisplayOverrides(
        entrypoint_node_id=UUID("79145e96-23c3-4763-ad7e-f3c6529fe535"),
        entrypoint_node_source_handle_id=UUID("b4b974ea-716d-4187-a5fb-808284272fe2"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-914.495748855461, y=126.402223675605, zoom=0.6256812731632875)
        ),
    )
    inputs_display = {
        Inputs.items: WorkflowInputsVellumDisplayOverrides(
            id=UUID("b8d66997-444e-4409-b315-5bef0c06192a"), name="items", required=True
        ),
        Inputs.item: WorkflowInputsVellumDisplayOverrides(
            id=UUID("2619e147-870f-40ec-8f21-f3e131fcd65a"), name="item", required=True
        ),
        Inputs.index: WorkflowInputsVellumDisplayOverrides(
            id=UUID("edecf894-c35b-485a-998f-118833a4b045"), name="index", required=True
        ),
    }
    entrypoint_displays = {
        TemplatingNode: EntrypointVellumDisplayOverrides(
            id=UUID("79145e96-23c3-4763-ad7e-f3c6529fe535"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("09c7b24f-a133-4c71-971a-15b696abfe32")),
        )
    }
    edge_displays = {
        (TemplatingNode.Ports.default, SearchNode): EdgeVellumDisplayOverrides(
            id=UUID("d9cc06ea-07fb-413e-b11d-619e29dfbf84")
        ),
        (SearchNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("41499fe7-2ec8-4f35-9fd7-34cb26e57464")
        ),
    }
    output_displays = {
        MapNodeWorkflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("bffc4749-00b8-44db-90ee-db655cbc7e62"), name="final-output"
        )
    }
