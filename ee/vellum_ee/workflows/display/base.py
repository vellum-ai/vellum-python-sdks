from dataclasses import dataclass
from uuid import UUID
from typing import TypeVar


@dataclass
class WorkflowMetaDisplayOverrides:
    pass


@dataclass
class WorkflowMetaDisplay(WorkflowMetaDisplayOverrides):
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
class EdgeDisplayOverrides:
    id: UUID


@dataclass
class EdgeDisplay(EdgeDisplayOverrides):
    pass


EdgeDisplayType = TypeVar("EdgeDisplayType", bound=EdgeDisplay)
EdgeDisplayOverridesType = TypeVar("EdgeDisplayOverridesType", bound=EdgeDisplayOverrides)


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
