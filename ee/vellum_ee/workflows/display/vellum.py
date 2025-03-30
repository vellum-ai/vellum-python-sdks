from dataclasses import dataclass
from uuid import UUID
from typing import List, Literal, Optional

from vellum.core import UniversalBaseModel
from vellum_ee.workflows.display.base import (
    EdgeDisplayOverrides,
    EntrypointDisplayOverrides,
    StateValueDisplayOverrides,
    WorkflowInputsDisplay,
    WorkflowInputsDisplayOverrides,
    WorkflowMetaDisplayOverrides,
    WorkflowOutputDisplayOverrides,
)
from vellum_ee.workflows.display.base import WorkflowDisplayData  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.base import WorkflowDisplayDataViewport  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.editor.types import NodeDisplayComment  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.editor.types import NodeDisplayPosition  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.utils.vellum import NodeInputValuePointerRule


class CodeResourceDefinition(UniversalBaseModel):
    name: str
    module: List[str]


@dataclass
class WorkflowMetaVellumDisplayOverrides(WorkflowMetaDisplayOverrides):
    """
    DEPRECATED: Use WorkflowMetaDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class WorkflowMetaVellumDisplay(WorkflowMetaVellumDisplayOverrides):
    """
    DEPRECATED: Use WorkflowMetaDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class WorkflowInputsVellumDisplayOverrides(WorkflowInputsDisplay, WorkflowInputsDisplayOverrides):
    name: Optional[str] = None
    required: Optional[bool] = None
    color: Optional[str] = None


@dataclass
class WorkflowInputsVellumDisplay(WorkflowInputsVellumDisplayOverrides):
    pass


@dataclass
class StateValueVellumDisplayOverrides(StateValueDisplayOverrides):
    """
    DEPRECATED: Use StateValueDisplay instead. Will be removed in 0.15.0
    """

    required: Optional[bool] = None


@dataclass
class StateValueVellumDisplay(StateValueVellumDisplayOverrides):
    """
    DEPRECATED: Use StateValueDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class EdgeVellumDisplayOverrides(EdgeDisplayOverrides):
    """
    DEPRECATED: Use EdgeDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class EdgeVellumDisplay(EdgeVellumDisplayOverrides):
    """
    DEPRECATED: Use EdgeDisplay instead. Will be removed in 0.15.0
    """

    source_node_id: UUID
    source_handle_id: UUID
    target_node_id: UUID
    target_handle_id: UUID
    type: Literal["DEFAULT"] = "DEFAULT"


@dataclass
class EntrypointVellumDisplayOverrides(EntrypointDisplayOverrides):
    """
    DEPRECATED: Use EntrypointDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class EntrypointVellumDisplay(EntrypointVellumDisplayOverrides):
    """
    DEPRECATED: Use EntrypointDisplay instead. Will be removed in 0.15.0
    """

    pass


@dataclass
class WorkflowOutputVellumDisplayOverrides(WorkflowOutputDisplayOverrides):
    """
    DEPRECATED: Use WorkflowOutputDisplay instead. Will be removed in 0.15.0
    """

    label: Optional[str] = None
    node_id: Optional[UUID] = None
    display_data: Optional[NodeDisplayData] = None
    target_handle_id: Optional[UUID] = None


@dataclass
class WorkflowOutputVellumDisplay(WorkflowOutputVellumDisplayOverrides):
    """
    DEPRECATED: Use WorkflowOutputDisplay instead. Will be removed in 0.15.0
    """

    pass


class NodeInputValuePointer(UniversalBaseModel):
    rules: List[NodeInputValuePointerRule]
    combinator: Literal["OR"] = "OR"


class NodeInput(UniversalBaseModel):
    id: str
    key: str
    value: NodeInputValuePointer
