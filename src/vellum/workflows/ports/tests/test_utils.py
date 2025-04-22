import pytest

from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.ports.utils import validate_ports

ERROR_MESSAGE = "Port conditions must be in the following order: on_if, on_elif, on_else"


class Inputs(BaseInputs):
    value: str


def test_valid_single_if_else_group():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_if(Inputs.value.equals("Hello"))
            branch_3 = Port.on_else()

    ports = [port for port in TestNode.Ports]
    result = validate_ports(ports)

    assert result is True


def test_valid_single_if_elif_else_group():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_if(Inputs.value.equals("Hello"))
            branch_2 = Port.on_elif(Inputs.value.equals("Hello"))
            branch_3 = Port.on_else()

    ports = [port for port in TestNode.Ports]
    result = validate_ports(ports)

    assert result is True


def test_valid_multiple_if_else_group():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_if(Inputs.value.equals("Hello"))
            branch_2 = Port.on_else()
            branch_3 = Port.on_if(Inputs.value.equals("Hello"))
            branch_4 = Port.on_else()

    ports = [port for port in TestNode.Ports]
    result = validate_ports(ports)

    assert result is True


def test_valid_multiple_if_elif_else_group():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_if(Inputs.value.equals("Hello"))
            branch_2 = Port.on_elif(Inputs.value.equals("Hello"))
            branch_3 = Port.on_else()
            branch_4 = Port.on_if(Inputs.value.equals("Hello"))
            branch_5 = Port.on_elif(Inputs.value.equals("Hello"))
            branch_6 = Port.on_else()

    ports = [port for port in TestNode.Ports]
    result = validate_ports(ports)

    assert result is True


def test_invalid_single_if_else_group():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_else()
            branch_2 = Port.on_if(Inputs.value.equals("Hello"))

    ports = [port for port in TestNode.Ports]

    with pytest.raises(ValueError) as exc_info:
        validate_ports(ports)

    assert str(exc_info.value) == ERROR_MESSAGE


def test_invalid_single_if_elif_else_group():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_else()
            branch_2 = Port.on_if(Inputs.value.equals("Hello"))
            branch_3 = Port.on_elif(Inputs.value.equals("Hello"))

    ports = [port for port in TestNode.Ports]

    with pytest.raises(ValueError) as exc_info:
        validate_ports(ports)

    assert str(exc_info.value) == ERROR_MESSAGE


def test_invalid_multiple_if_elif_else_groups():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_if(Inputs.value.equals("Hello"))
            branch_2 = Port.on_elif(Inputs.value.equals("Hi"))
            branch_3 = Port.on_else()
            branch_4 = Port.on_elif(Inputs.value.equals("Greetings"))
            branch_5 = Port.on_if(Inputs.value.equals("World"))

    ports = [port for port in TestNode.Ports]

    with pytest.raises(ValueError) as exc_info:
        validate_ports(ports)

    assert str(exc_info.value) == ERROR_MESSAGE


def test_invalid_single_if_else_group_multiple_else():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_if(Inputs.value.equals("Hello"))
            branch_2 = Port.on_else()
            branch_3 = Port.on_else()
            branch_4 = Port.on_if(Inputs.value.equals("World"))

    ports = [port for port in TestNode.Ports]

    with pytest.raises(ValueError) as exc_info:
        validate_ports(ports)

    assert str(exc_info.value) == f"Class {ports[0].node_class}.Ports must have at most one on_else condition"


def test_invalid_single_if_else_group_multiple_if():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_1 = Port.on_if(Inputs.value.equals("Hello"))
            branch_2 = Port.on_if(Inputs.value.equals("Hello"))
            branch_3 = Port.on_else()

    ports = [port for port in TestNode.Ports]

    with pytest.raises(ValueError) as exc_info:
        validate_ports(ports)

    assert (
        str(exc_info.value)
        == f"Class {ports[0].node_class}.Ports must have exactly one on_if condition and exactly one on_else condition"
    )


def test_invalid_single_elif_else_group_multiple_elif():
    class TestNode(BaseNode):
        class Ports(BaseNode.Ports):
            branch_2 = Port.on_elif(Inputs.value.equals("Hello"))
            branch_3 = Port.on_elif(Inputs.value.equals("Hello"))
            branch_4 = Port.on_else()

    ports = [port for port in TestNode.Ports]

    with pytest.raises(ValueError) as exc_info:
        validate_ports(ports)

    assert str(exc_info.value) == "Port conditions must be in the following order: on_if, on_elif, on_else"
