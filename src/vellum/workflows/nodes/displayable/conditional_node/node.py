from typing import Set

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.ports.node_ports import NodePorts
from vellum.workflows.ports.port import Port
from vellum.workflows.ports.utils import validate_ports
from vellum.workflows.state.base import BaseState
from vellum.workflows.types import MergeBehavior


class ConditionalNode(BaseNode):
    """
    Used to conditionally determine which port to invoke next. This node exists to be backwards compatible with
    Vellum's Conditional Node, and for most cases, you should extend `BaseNode.Ports` directly.
    """

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Ports(NodePorts):
        def __call__(self, outputs: BaseOutputs, state: BaseState) -> Set[Port]:
            all_ports = [port for port in self.__class__]
            enforce_single_invoked_port = validate_ports(all_ports)

            if not enforce_single_invoked_port:
                raise ValueError("Conditional nodes must have exactly one if port")

            return super().__call__(outputs, state)
