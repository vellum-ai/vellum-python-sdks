from dataclasses import dataclass
from uuid import UUID
from typing import Optional, TypeVar


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
    required: Optional[bool] = None
    color: Optional[str] = None


@dataclass
class WorkflowInputsDisplay(WorkflowInputsDisplayOverrides):
    pass


WorkflowInputsDisplayType = TypeVar("WorkflowInputsDisplayType", bound=WorkflowInputsDisplay)
WorkflowInputsDisplayOverridesType = TypeVar("WorkflowInputsDisplayOverridesType", bound=WorkflowInputsDisplayOverrides)


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
class WorkflowOutputDisplayOverrides:
    id: UUID


@dataclass
class WorkflowOutputDisplay(WorkflowOutputDisplayOverrides):
    pass


WorkflowOutputDisplayType = TypeVar("WorkflowOutputDisplayType", bound=WorkflowOutputDisplay)
WorkflowOutputDisplayOverridesType = TypeVar("WorkflowOutputDisplayOverridesType", bound=WorkflowOutputDisplayOverrides)
