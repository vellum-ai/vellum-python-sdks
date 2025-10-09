from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID
from typing import TYPE_CHECKING, Dict, Optional, Type

from pydantic import Field

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.editor.types import NodeDisplayData

if TYPE_CHECKING:
    from vellum.workflows.triggers.base import BaseTrigger


class WorkflowTriggerType(Enum):
    MANUAL = "MANUAL"
    SLACK_MESSAGE = "SLACK_MESSAGE"


def get_trigger_type_mapping() -> Dict[Type["BaseTrigger"], WorkflowTriggerType]:
    """
    Get mapping from trigger classes to their WorkflowTriggerType enum values.

    This is a function to avoid circular imports - it imports trigger classes
    only when called, not at module load time.

    Returns:
        Dictionary mapping trigger classes to their enum types
    """
    from vellum.workflows.triggers.manual import ManualTrigger
    from vellum.workflows.triggers.slack import SlackTrigger

    return {
        ManualTrigger: WorkflowTriggerType.MANUAL,
        SlackTrigger: WorkflowTriggerType.SLACK_MESSAGE,
    }


class WorkflowDisplayDataViewport(UniversalBaseModel):
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0


class WorkflowDisplayData(UniversalBaseModel):
    viewport: WorkflowDisplayDataViewport = Field(default_factory=WorkflowDisplayDataViewport)


@dataclass
class WorkflowMetaDisplay:
    entrypoint_node_id: UUID
    entrypoint_node_source_handle_id: UUID
    entrypoint_node_display: NodeDisplayData = Field(default_factory=NodeDisplayData)
    display_data: WorkflowDisplayData = field(default_factory=WorkflowDisplayData)

    @classmethod
    def get_default(cls, workflow: Type[BaseWorkflow]) -> "WorkflowMetaDisplay":
        entrypoint_node_id = uuid4_from_hash(f"{workflow.__id__}|entrypoint_node_id")
        entrypoint_node_source_handle_id = uuid4_from_hash(f"{workflow.__id__}|entrypoint_node_source_handle_id")

        return WorkflowMetaDisplay(
            entrypoint_node_id=entrypoint_node_id,
            entrypoint_node_source_handle_id=entrypoint_node_source_handle_id,
            entrypoint_node_display=NodeDisplayData(),
        )


@dataclass
class WorkflowInputsDisplay:
    id: UUID
    name: Optional[str] = None
    color: Optional[str] = None


@dataclass
class StateValueDisplay:
    id: UUID
    name: Optional[str] = None
    color: Optional[str] = None


@dataclass
class EdgeDisplay:
    id: UUID
    z_index: Optional[int] = None


@dataclass
class EntrypointDisplay:
    id: UUID
    edge_display: EdgeDisplay


@dataclass
class WorkflowOutputDisplay:
    id: UUID
    name: str
