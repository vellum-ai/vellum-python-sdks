from typing import Any, Dict, Iterator, Optional, Set, Tuple, Type

from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.ports.utils import get_port_groups, validate_ports
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import ConditionType


class _NodePortsMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        for k, v in dct.items():
            if k.startswith("_"):
                continue
            if not isinstance(v, Port):
                raise ValueError(f"All fields in {name} must be of type Port. Received: {v.__class__}")

        return super().__new__(mcs, name, bases, dct)

    def __iter__(cls) -> Iterator[Port]:
        for attr_name, attr_value in cls.__dict__.items():
            if not attr_name.startswith("_") and isinstance(attr_value, Port):
                yield attr_value

    @property
    def _default_port(cls) -> Optional[Port]:
        default_ports = [port for port in cls if port.default]

        if len(default_ports) > 1:
            raise ValueError(f"Class {cls.__name__} must have only one default port")

        return default_ports[0] if default_ports else None


class NodePorts(metaclass=_NodePortsMeta):
    def __call__(self, outputs: BaseOutputs, state: BaseState) -> Set[Port]:
        """
        Invokes the appropriate ports based on the fulfilled outputs and state.
        """

        invoked_ports: Set[Port] = set()
        all_ports = [port for port in self.__class__]
        enforce_single_invoked_conditional_port = validate_ports(all_ports)

        for port in all_ports:
            if port._condition_type == ConditionType.IF:
                resolved_condition = port.resolve_condition(state)
                if resolved_condition:
                    invoked_ports.add(port)
                    if enforce_single_invoked_conditional_port:
                        break

            elif port._condition_type == ConditionType.ELIF:
                resolved_condition = port.resolve_condition(state)
                if resolved_condition:
                    invoked_ports.add(port)
                    if len(get_port_groups(all_ports)) <= 1:
                        break

            elif port._condition_type == ConditionType.ELSE and not invoked_ports:
                invoked_ports.add(port)
                break

        if not invoked_ports:
            default_port = self.__class__._default_port
            if default_port:
                invoked_ports.add(default_port)

        return invoked_ports

    def __lt__(self, output: BaseOutput) -> Set[Port]:
        """
        Invokes the appropriate ports based on the streamed output
        """

        return set()
