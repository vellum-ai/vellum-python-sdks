from dataclasses import dataclass, field
from enum import Enum
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
    WorkflowMetaDisplay,
    WorkflowMetaDisplayOverrides,
    WorkflowOutputDisplayOverrides,
)


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


class WorkflowDisplayDataViewport(UniversalBaseModel):
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0


class WorkflowDisplayData(UniversalBaseModel):
    viewport: WorkflowDisplayDataViewport = Field(default_factory=WorkflowDisplayDataViewport)


@dataclass
class WorkflowMetaVellumDisplayOverrides(WorkflowMetaDisplay, WorkflowMetaDisplayOverrides):
    entrypoint_node_id: UUID
    entrypoint_node_source_handle_id: UUID
    entrypoint_node_display: NodeDisplayData
    display_data: WorkflowDisplayData = field(default_factory=WorkflowDisplayData)


@dataclass
class WorkflowMetaVellumDisplay(WorkflowMetaVellumDisplayOverrides):
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


class LogicalOperator(str, Enum):
    EQUALS = "equals"
    DOES_NOT_EQUAL = "does_not_equal"
    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"
    LESS_THAN_OR_EQUAL_TO = "less_than_or_equal_to"
    GREATER_THAN_OR_EQUAL_TO = "greater_than_or_equal_to"
    CONTAINS = "contains"
    BEGINS_WITH = "begins_with"
    ENDS_WITH = "ends_with"
    DOES_NOT_CONTAIN = "does_not_contain"
    DOES_NOT_BEGIN_WITH = "does_not_begin_with"
    DOES_NOT_END_WITH = "does_not_end_with"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    PARSE_JSON = "parse_json"
    COALESCE = "coalesce"


class ConditionCombinator(str, Enum):
    OR = "OR"
    AND = "AND"


class NodeOutputWorkflowReference(UniversalBaseModel):
    type: Literal["NODE_OUTPUT"] = "NODE_OUTPUT"
    node_id: str
    node_output_id: str


class WorkflowInputWorkflowReference(UniversalBaseModel):
    type: Literal["WORKFLOW_INPUT"] = "WORKFLOW_INPUT"
    input_variable_id: str


class WorkflowStateVariableWorkflowReference(UniversalBaseModel):
    type: Literal["WORKFLOW_STATE"] = "WORKFLOW_STATE"
    state_variable_id: str


class ConstantValueWorkflowReference(UniversalBaseModel):
    type: Literal["CONSTANT_VALUE"] = "CONSTANT_VALUE"
    value: VellumValue


class VellumSecretWorkflowReference(UniversalBaseModel):
    type: Literal["VELLUM_SECRET"] = "VELLUM_SECRET"
    vellum_secret_name: str


class ExecutionCounterWorkflowReference(UniversalBaseModel):
    type: Literal["EXECUTION_COUNTER"] = "EXECUTION_COUNTER"
    node_id: str


class UnaryWorkflowExpression(UniversalBaseModel):
    type: Literal["UNARY_EXPRESSION"] = "UNARY_EXPRESSION"
    lhs: Optional["WorkflowValueDescriptor"] = None
    operator: LogicalOperator


class BinaryWorkflowExpression(UniversalBaseModel):
    type: Literal["BINARY_EXPRESSION"] = "BINARY_EXPRESSION"
    lhs: Optional["WorkflowValueDescriptor"] = None
    operator: LogicalOperator
    rhs: Optional["WorkflowValueDescriptor"] = None


class TernaryWorkflowExpression(UniversalBaseModel):
    type: Literal["TERNARY_EXPRESSION"] = "TERNARY_EXPRESSION"
    base: Optional["WorkflowValueDescriptor"] = None
    operator: LogicalOperator
    lhs: Optional["WorkflowValueDescriptor"] = None
    rhs: Optional["WorkflowValueDescriptor"] = None


WorkflowValueDescriptorReference = Union[
    NodeOutputWorkflowReference,
    WorkflowInputWorkflowReference,
    WorkflowStateVariableWorkflowReference,
    ConstantValueWorkflowReference,
    VellumSecretWorkflowReference,
    ExecutionCounterWorkflowReference,
]

WorkflowExpression = Union[
    UnaryWorkflowExpression,
    BinaryWorkflowExpression,
    TernaryWorkflowExpression,
]

WorkflowValueDescriptor = Union[
    WorkflowExpression,
    WorkflowValueDescriptorReference,
]


class NodeOutput(UniversalBaseModel):
    id: str
    name: str
    type: VellumVariableType
    value: Optional[WorkflowValueDescriptor] = None


class NodeAttribute(UniversalBaseModel):
    id: str
    name: str
    value: Optional[WorkflowValueDescriptor] = None


class AdornmentNode(UniversalBaseModel):
    id: str
    label: str
    base: CodeResourceDefinition
    attributes: List[NodeAttribute]
