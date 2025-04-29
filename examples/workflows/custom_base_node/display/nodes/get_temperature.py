from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.get_temperature import GetTemperature


class GetTemperatureDisplay(BaseNodeDisplay[GetTemperature]):
    port_displays = {
        GetTemperature.Ports.default: PortDisplayOverrides(id=UUID("3f774189-4e8e-45b6-a6eb-f62a7a96593c"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)
