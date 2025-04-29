from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.echo_request import EchoRequest


class EchoRequestDisplay(BaseNodeDisplay[EchoRequest]):
    port_displays = {EchoRequest.Ports.default: PortDisplayOverrides(id=UUID("615b3eb7-f1e3-4f23-9743-9a90044d9500"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)
