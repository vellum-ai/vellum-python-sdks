from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.check_tag_node import CheckTagNode


class CheckTagNodeDisplay(BaseNodeDisplay[CheckTagNode]):
    label = "CheckTagNode"
    node_id = UUID("aca36e9b-c0dc-4435-ae28-8a67ffdc20ce")
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1547.0109111320066, y=-349.9265612114595),
        z_index=11,
        icon="vellum:icon:square",
        color="peach",
    )
    attribute_ids_by_name = {"message_text": UUID("526e4da2-804e-4016-ae41-1b25e52852d8")}
    output_display = {
        CheckTagNode.Outputs.is_tagged: NodeOutputDisplay(
            id=UUID("d013de82-2f2d-494a-bc9e-2e2e2c514389"), name="is_tagged"
        ),
        CheckTagNode.Outputs.message_text: NodeOutputDisplay(
            id=UUID("526e4da2-804e-4016-ae41-1b25e52852d8"), name="message_text"
        ),
    }
    port_displays = {
        CheckTagNode.Ports.tagged: PortDisplayOverrides(id=UUID("0dbd4095-eee9-4bd3-9259-704ed9dc7de0")),
        CheckTagNode.Ports.not_tagged: PortDisplayOverrides(id=UUID("ba865c56-f14b-4b61-b539-c32689aa7cbe")),
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1547.0109111320066, y=-349.9265612114595),
        z_index=11,
        icon="vellum:icon:square",
        color="peach",
    )
