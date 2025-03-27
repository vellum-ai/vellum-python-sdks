from dataclasses import dataclass
from uuid import UUID
from typing import List, Literal, Optional, Union

from pydantic import Field

from vellum import VellumVariableType
from vellum.client.types.array_vellum_value import ArrayVellumValue
from vellum.client.types.vellum_value import VellumValue
from vellum.core import UniversalBaseModel
from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EdgeDisplayOverrides,
    EntrypointDisplay,
    EntrypointDisplayOverrides,
    StateValueDisplay,
    StateValueDisplayOverrides,
    WorkflowInputsDisplay,
    WorkflowInputsDisplayOverrides,
    WorkflowMetaDisplayOverrides,
    WorkflowOutputDisplayOverrides,
)
from vellum_ee.workflows.display.base import WorkflowDisplayData  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.base import WorkflowDisplayDataViewport  # noqa: F401 - Remove in 0.15.0


class NodeDisplayPosition(UniversalBaseModel):
    x: float = 0.0
    y: float = 0.0


class NodeDisplayComment(UniversalBaseModel):
    value: Optional[str] = None
    expanded: Optional[bool] = None


class NodeDisplayData(UniversalBaseModel):
    position: NodeDisplayPosition = Field(default_factory=NodeDisplayPosition)
    width: Optional[int] = None
    height: Optional[int] = None
    comment: Optional[NodeDisplayComment] = None


class CodeResourceDefinition(UniversalBaseModel):
    name: str
    module: List[str]


@dataclass
class WorkflowMetaVellumDisplayOverrides(WorkflowMetaDisplayOverrides):
    entrypoint_node_display: NodeDisplayData = Field(default_factory=NodeDisplayData)


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
class StateValueVellumDisplayOverrides(StateValueDisplay, StateValueDisplayOverrides):
    name: Optional[str] = None
    required: Optional[bool] = None
    color: Optional[str] = None


@dataclass
class StateValueVellumDisplay(StateValueVellumDisplayOverrides):
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
class EntrypointVellumDisplayOverrides(EntrypointDisplay, EntrypointDisplayOverrides):
    edge_display: EdgeDisplay


@dataclass
class EntrypointVellumDisplay(EntrypointVellumDisplayOverrides):
    edge_display: EdgeDisplay


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


class ConstantValuePointer(UniversalBaseModel):
    type: Literal["CONSTANT_VALUE"] = "CONSTANT_VALUE"
    data: VellumValue


ArrayVellumValue.model_rebuild()


class NodeOutputData(UniversalBaseModel):
    node_id: str
    output_id: str


class NodeOutputPointer(UniversalBaseModel):
    type: Literal["NODE_OUTPUT"] = "NODE_OUTPUT"
    data: NodeOutputData


class InputVariableData(UniversalBaseModel):
    input_variable_id: str


class InputVariablePointer(UniversalBaseModel):
    type: Literal["INPUT_VARIABLE"] = "INPUT_VARIABLE"
    data: InputVariableData


class WorkspaceSecretData(UniversalBaseModel):
    type: VellumVariableType
    workspace_secret_id: Optional[str] = None


class WorkspaceSecretPointer(UniversalBaseModel):
    type: Literal["WORKSPACE_SECRET"] = "WORKSPACE_SECRET"
    data: WorkspaceSecretData


class ExecutionCounterData(UniversalBaseModel):
    node_id: str


class ExecutionCounterPointer(UniversalBaseModel):
    type: Literal["EXECUTION_COUNTER"] = "EXECUTION_COUNTER"
    data: ExecutionCounterData


NodeInputValuePointerRule = Union[
    NodeOutputPointer,
    InputVariablePointer,
    ConstantValuePointer,
    WorkspaceSecretPointer,
    ExecutionCounterPointer,
]


class NodeInputValuePointer(UniversalBaseModel):
    rules: List[NodeInputValuePointerRule]
    combinator: Literal["OR"] = "OR"


class NodeInput(UniversalBaseModel):
    id: str
    key: str
    value: NodeInputValuePointer
