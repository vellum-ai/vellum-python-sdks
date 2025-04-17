from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, Type

from pydantic import Field

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.editor.types import NodeDisplayData


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
class WorkflowMetaDisplayOverrides(WorkflowMetaDisplay):
    """
    DEPRECATED: Use WorkflowMetaDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class WorkflowInputsDisplay:
    id: UUID
    name: Optional[str] = None
    color: Optional[str] = None


@dataclass
class WorkflowInputsDisplayOverrides(WorkflowInputsDisplay):
    """
    DEPRECATED: Use WorkflowInputsDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class StateValueDisplay:
    id: UUID
    name: Optional[str] = None
    color: Optional[str] = None


@dataclass
class StateValueDisplayOverrides(StateValueDisplay):
    """
    DEPRECATED: Use StateValueDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class EdgeDisplay:
    id: UUID


@dataclass
class EdgeDisplayOverrides(EdgeDisplay):
    """
    DEPRECATED: Use EdgeDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class EntrypointDisplay:
    id: UUID
    edge_display: EdgeDisplay


@dataclass
class EntrypointDisplayOverrides(EntrypointDisplay):
    """
    DEPRECATED: Use EntrypointDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class WorkflowOutputDisplay:
    id: UUID
    name: str


@dataclass
class WorkflowOutputDisplayOverrides(WorkflowOutputDisplay):
    """
    DEPRECATED: Use WorkflowOutputDisplay instead. Will be removed in 0.15.0
    """

    pass
