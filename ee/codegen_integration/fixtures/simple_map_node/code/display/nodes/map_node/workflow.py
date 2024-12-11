from uuid import UUID

from vellum_ee.workflows.display.vellum import (
    EdgeVellumDisplayOverrides,
    EntrypointVellumDisplayOverrides,
    NodeDisplayData,
    NodeDisplayPosition,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsVellumDisplayOverrides,
    WorkflowMetaVellumDisplayOverrides,
    WorkflowOutputVellumDisplayOverrides,
)
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay

from ....nodes.map_node.inputs import Inputs
from ....nodes.map_node.nodes.final_output import FinalOutput
from ....nodes.map_node.nodes.search_node import SearchNode
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
            id=UUID("b8d66997-444e-4409-b315-5bef0c06192a"), required=True
        ),
        Inputs.item: WorkflowInputsVellumDisplayOverrides(
            id=UUID("2619e147-870f-40ec-8f21-f3e131fcd65a"), required=True
        ),
        Inputs.index: WorkflowInputsVellumDisplayOverrides(
            id=UUID("edecf894-c35b-485a-998f-118833a4b045"), required=True
        ),
    }
    entrypoint_displays = {
        SearchNode: EntrypointVellumDisplayOverrides(
            id=UUID("79145e96-23c3-4763-ad7e-f3c6529fe535"),
            edge_display=EdgeVellumDisplayOverrides(id=UUID("09c7b24f-a133-4c71-971a-15b696abfe32")),
        )
    }
    edge_displays = {
        (SearchNode.Ports.default, FinalOutput): EdgeVellumDisplayOverrides(
            id=UUID("d9cc06ea-07fb-413e-b11d-619e29dfbf84")
        )
    }
    output_displays = {
        MapNodeWorkflow.Outputs.final_output: WorkflowOutputVellumDisplayOverrides(
            id=UUID("bffc4749-00b8-44db-90ee-db655cbc7e62"),
            node_id=UUID("d9d29911-dd45-45d5-9ac8-1a06bb596c2f"),
            node_input_id=UUID("18dddbce-025b-461c-aa7a-ab2561739521"),
            name="final-output",
            label="Final Output",
            target_handle_id=UUID("8ff89a09-6ff0-4b02-bba7-eb8456a9c865"),
            display_data=NodeDisplayData(position=NodeDisplayPosition(x=2750, y=210), width=463, height=234),
            edge_id=UUID("d9cc06ea-07fb-413e-b11d-619e29dfbf84"),
        )
    }
