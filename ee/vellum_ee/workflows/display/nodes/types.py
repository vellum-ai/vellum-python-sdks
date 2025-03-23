from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from vellum_ee.workflows.display.vellum import WorkflowValueDescriptor


@dataclass
class NodeOutputDisplay:
    id: UUID
    name: str


@dataclass
class NodeInputDisplay:
    id: UUID
    name: str
    type: Optional[str] = None
    value: Optional[WorkflowValueDescriptor] = None


@dataclass
class PortDisplayOverrides:
    id: UUID


@dataclass
class PortDisplay(PortDisplayOverrides):
    node_id: UUID
