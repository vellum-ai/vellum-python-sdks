from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides

from ...nodes.fibonacci import Fibonacci


class FibonacciDisplay(BaseNodeDisplay[Fibonacci]):
    port_displays = {Fibonacci.Ports.default: PortDisplayOverrides(id=UUID("bfb5c1da-5cf0-40bf-adce-c071f0d09d12"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)
