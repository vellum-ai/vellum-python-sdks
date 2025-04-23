from collections import Counter
from typing import List

from vellum.workflows.ports.port import Port
from vellum.workflows.types.core import ConditionType

PORT_TYPE_PRIORITIES = {
    ConditionType.IF: 1,
    ConditionType.ELIF: 2,
    ConditionType.ELSE: 3,
}


def get_port_groups(ports: List[Port]) -> List[List[ConditionType]]:
    # We don't want to validate ports with no condition (default ports)
    port_types = [port._condition_type for port in ports if port._condition_type is not None]

    ports_class = f"{ports[0].node_class}.Ports"

    # Check all ports by port groups
    port_groups: List[List[ConditionType]] = []
    current_port_group: List[ConditionType] = []

    for port_type in port_types:
        # Start a new group only if we see an IF
        if port_type == ConditionType.IF:
            # Only append the current group if it's not empty and starts with an IF
            if current_port_group and current_port_group[0] == ConditionType.IF:
                port_groups.append(current_port_group)
            current_port_group = [port_type]
        else:
            # If we see an ELIF or ELSE without a preceding IF, that's an error
            if not current_port_group:
                raise ValueError(f"Class {ports_class} must have ports in the following order: on_if, on_elif, on_else")
            current_port_group.append(port_type)

    if current_port_group and current_port_group[0] == ConditionType.IF:
        port_groups.append(current_port_group)
    elif current_port_group:
        # If the last group doesn't start with IF, that's an error
        raise ValueError(f"Class {ports_class} must have ports in the following order: on_if, on_elif, on_else")

    return port_groups


def validate_ports(ports: List[Port]) -> bool:
    ports_class = f"{ports[0].node_class}.Ports"
    port_groups = get_port_groups(ports)
    # Validate each port group
    for group in port_groups:
        # Check that each port group is in the correct order
        sorted_group = sorted(group, key=lambda port_type: PORT_TYPE_PRIORITIES[port_type])
        if sorted_group != group:
            raise ValueError(f"Class {ports_class} must have ports in the following order: on_if, on_elif, on_else")

        # Count the types in this port group
        counter = Counter(group)
        number_of_if_ports = counter[ConditionType.IF]
        number_of_elif_ports = counter[ConditionType.ELIF]
        number_of_else_ports = counter[ConditionType.ELSE]

        # Apply the rules to each port group
        if number_of_if_ports != 1:
            raise ValueError(f"Class {ports_class} must have exactly one on_if condition")

        if number_of_elif_ports > 0 and number_of_if_ports != 1:
            raise ValueError(f"Class {ports_class} containing on_elif ports must have exactly one on_if condition")

        if number_of_else_ports > 1:
            raise ValueError(f"Class {ports_class} must have at most one on_else condition")

    enforce_single_invoked_conditional_port = len(port_groups) <= 1
    return enforce_single_invoked_conditional_port
