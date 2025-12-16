from dataclasses import dataclass
from uuid import UUID


@dataclass
class NodeOutputDisplay:
    id: UUID
    name: str
    _is_implicit: bool = False


@dataclass
class PortDisplayOverrides:
    id: UUID


@dataclass
class PortDisplay(PortDisplayOverrides):
    node_id: UUID
