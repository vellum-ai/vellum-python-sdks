from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, TypeVar

from pydantic import Field

from vellum.client.core.pydantic_utilities import UniversalBaseModel
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


@dataclass
class WorkflowMetaDisplayOverrides(WorkflowMetaDisplay):
    """
    DEPRECATED: Use WorkflowMetaDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class WorkflowInputsDisplayOverrides:
    id: UUID


@dataclass
class WorkflowInputsDisplay(WorkflowInputsDisplayOverrides):
    pass


WorkflowInputsDisplayType = TypeVar("WorkflowInputsDisplayType", bound=WorkflowInputsDisplay)
WorkflowInputsDisplayOverridesType = TypeVar("WorkflowInputsDisplayOverridesType", bound=WorkflowInputsDisplayOverrides)


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
