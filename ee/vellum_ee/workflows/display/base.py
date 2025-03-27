from dataclasses import dataclass, field
from uuid import UUID
from typing import TypeVar

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


WorkflowMetaDisplayType = TypeVar("WorkflowMetaDisplayType", bound=WorkflowMetaDisplay)
WorkflowMetaDisplayOverridesType = TypeVar("WorkflowMetaDisplayOverridesType", bound=WorkflowMetaDisplayOverrides)


@dataclass
class WorkflowInputsDisplayOverrides:
    id: UUID


@dataclass
class WorkflowInputsDisplay(WorkflowInputsDisplayOverrides):
    pass


WorkflowInputsDisplayType = TypeVar("WorkflowInputsDisplayType", bound=WorkflowInputsDisplay)
WorkflowInputsDisplayOverridesType = TypeVar("WorkflowInputsDisplayOverridesType", bound=WorkflowInputsDisplayOverrides)


@dataclass
class StateValueDisplayOverrides:
    id: UUID


@dataclass
class StateValueDisplay(StateValueDisplayOverrides):
    pass


StateValueDisplayType = TypeVar("StateValueDisplayType", bound=StateValueDisplay)
StateValueDisplayOverridesType = TypeVar("StateValueDisplayOverridesType", bound=StateValueDisplayOverrides)


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
class EntrypointDisplayOverrides:
    id: UUID


@dataclass
class EntrypointDisplay(EntrypointDisplayOverrides):
    pass


EntrypointDisplayType = TypeVar("EntrypointDisplayType", bound=EntrypointDisplay)
EntrypointDisplayOverridesType = TypeVar("EntrypointDisplayOverridesType", bound=EntrypointDisplayOverrides)


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
