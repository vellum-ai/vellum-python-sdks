from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.conditional_router import ConditionalRouter


class ConditionalRouterDisplay(BaseNodeDisplay[ConditionalRouter]):
    port_displays = {
        ConditionalRouter.Ports.exit: PortDisplayOverrides(id=UUID("4614e935-1a99-48c5-a3dd-46d4d97a883a")),
        ConditionalRouter.Ports.get_temperature: PortDisplayOverrides(id=UUID("1ba9260f-39b3-48f0-a1c9-a042346fb961")),
        ConditionalRouter.Ports.echo_request: PortDisplayOverrides(id=UUID("2834c6c6-0bbc-4d76-becd-de6abdbe0410")),
        ConditionalRouter.Ports.fibonacci: PortDisplayOverrides(id=UUID("ce38e395-c5a4-4550-b950-8994dff781b2")),
        ConditionalRouter.Ports.unknown: PortDisplayOverrides(id=UUID("c094a2db-3d76-46ee-8d44-eb255402e32d")),
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)
