# flake8: noqa: F401, F403

from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseMapNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ....nodes.invoke_functions import InvokeFunctions
from .nodes import *
from .workflow import *


class InvokeFunctionsDisplay(BaseMapNodeDisplay[InvokeFunctions]):
    label = "Invoke Functions"
    node_id = UUID("dd0cb554-14e8-43fc-ac45-a00edc5ec1cd")
    target_handle_id = UUID("628a2305-f870-4605-ac77-174c67837687")
    node_input_ids_by_name = {"items": UUID("98ee5b96-8446-4cd6-90c7-2141432ff0b6")}
    output_display = {
        InvokeFunctions.Outputs.final_output: NodeOutputDisplay(
            id=UUID("fe14414b-f4de-4f26-9339-63e3fab65ce8"), name="final-output"
        )
    }
    port_displays = {
        InvokeFunctions.Ports.default: PortDisplayOverrides(id=UUID("837c5b83-5602-40b8-9075-20669d02de4c"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3315.2439889794405, y=-104.74211423787813), width=None, height=None
    )
