from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID
from typing import Any, List, Literal, Optional, Union

from pydantic import Field

from vellum import ChatMessage, PromptParameters, SearchResult, SearchResultRequest, VellumVariable, VellumVariableType
from vellum.core import UniversalBaseModel
from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EdgeDisplayOverrides,
    EntrypointDisplay,
    EntrypointDisplayOverrides,
    WorkflowInputsDisplay,
    WorkflowInputsDisplayOverrides,
    WorkflowMetaDisplay,
    WorkflowMetaDisplayOverrides,
    WorkflowOutputDisplay,
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


class GenericNodeDisplayData(UniversalBaseModel):
    position: NodeDisplayPosition = Field(default_factory=NodeDisplayPosition)


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
class EdgeVellumDisplayOverrides(EdgeDisplay, EdgeDisplayOverrides):
    pass


@dataclass
class EdgeVellumDisplay(EdgeVellumDisplayOverrides):
    source_node_id: UUID
    source_handle_id: UUID
    target_node_id: UUID
    target_handle_id: UUID
    type: Literal["DEFAULT"] = "DEFAULT"


@dataclass
class EntrypointVellumDisplayOverrides(EntrypointDisplay, EntrypointDisplayOverrides):
    edge_display: EdgeVellumDisplayOverrides


@dataclass
class EntrypointVellumDisplay(EntrypointVellumDisplayOverrides):
    edge_display: EdgeVellumDisplay


@dataclass
class WorkflowOutputVellumDisplayOverrides(WorkflowOutputDisplay, WorkflowOutputDisplayOverrides):
    name: str
    label: str
    node_id: UUID
    node_input_id: UUID
    target_handle_id: UUID
    display_data: NodeDisplayData
    edge_id: UUID


@dataclass
class WorkflowOutputVellumDisplay(WorkflowOutputVellumDisplayOverrides):
    pass


class WorkflowNodeType(str, Enum):
    PROMPT = "PROMPT"
    TEMPLATING = "TEMPLATING"
    NOTE = "NOTE"
    CODE_EXECUTION = "CODE_EXECUTION"
    METRIC = "METRIC"
    SEARCH = "SEARCH"
    WEBHOOK = "WEBHOOK"
    MERGE = "MERGE"
    CONDITIONAL = "CONDITIONAL"
    API = "API"
    ENTRYPOINT = "ENTRYPOINT"
    TERMINAL = "TERMINAL"
    SUBWORKFLOW = "SUBWORKFLOW"
    MAP = "MAP"
    ERROR = "ERROR"


class StringVellumValue(UniversalBaseModel):
    type: Literal["STRING"] = "STRING"
    value: str


class NumberVellumValue(UniversalBaseModel):
    type: Literal["NUMBER"] = "NUMBER"
    value: Union[int, float]


class ChatHistoryVellumValue(UniversalBaseModel):
    type: Literal["CHAT_HISTORY"] = "CHAT_HISTORY"
    value: Union[List[ChatMessage], List[ChatMessage]]


class SearchResultsVellumValue(UniversalBaseModel):
    type: Literal["SEARCH_RESULTS"] = "SEARCH_RESULTS"
    value: Union[List[SearchResultRequest], List[SearchResult]]


class JsonVellumValue(UniversalBaseModel):
    type: Literal["JSON"] = "JSON"
    value: Optional[Any] = None


VellumValue = Union[
    StringVellumValue,
    NumberVellumValue,
    ChatHistoryVellumValue,
    SearchResultsVellumValue,
    JsonVellumValue,
]


class ConstantValuePointer(UniversalBaseModel):
    type: Literal["CONSTANT_VALUE"] = "CONSTANT_VALUE"
    data: VellumValue


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


class BaseWorkflowNode(UniversalBaseModel):
    id: str
    inputs: List[NodeInput]
    type: str
    display_data: Optional[NodeDisplayData] = None
    base: CodeResourceDefinition
    definition: CodeResourceDefinition


class EntrypointNodeData(UniversalBaseModel):
    source_handle_id: str


class EntrypointNode(BaseWorkflowNode):
    type: Literal[WorkflowNodeType.ENTRYPOINT] = WorkflowNodeType.ENTRYPOINT
    data: EntrypointNodeData


class PromptTemplateBlockData(UniversalBaseModel):
    version: Literal[1] = 1
    # blocks: List[PromptBlockRequest]


class PromptVersionExecConfig(UniversalBaseModel):
    parameters: PromptParameters
    input_variables: List[VellumVariable]
    prompt_template_block_data: PromptTemplateBlockData


class BasePromptNodeData(UniversalBaseModel):
    label: str
    output_id: str
    error_output_id: Optional[str] = None
    array_output_id: str
    source_handle_id: str
    target_handle_id: str


class InlinePromptNodeData(BasePromptNodeData):
    variant: Literal["INLINE"] = "INLINE"
    exec_config: PromptVersionExecConfig
    ml_model_name: str


class DeploymentPromptNodeData(BasePromptNodeData):
    variant: Literal["DEPLOYMENT"] = "DEPLOYMENT"
    deployment_id: str
    release_tag: str


PromptNodeData = Union[
    InlinePromptNodeData,
    DeploymentPromptNodeData,
]


class PromptNode(BaseWorkflowNode):
    type: Literal[WorkflowNodeType.PROMPT] = WorkflowNodeType.PROMPT
    data: PromptNodeData


class SearchNodeData(UniversalBaseModel):
    label: str

    results_output_id: str
    text_output_id: str
    error_output_id: Optional[str] = None

    source_handle_id: str
    target_handle_id: str

    query_node_input_id: str
    document_index_node_input_id: str
    weights_node_input_id: str
    limit_node_input_id: str
    separator_node_input_id: str
    result_merging_enabled_node_input_id: str
    external_id_filters_node_input_id: str
    metadata_filters_node_input_id: str


class SearchNode(BaseWorkflowNode):
    type: Literal[WorkflowNodeType.SEARCH] = WorkflowNodeType.SEARCH
    data: SearchNodeData


class FinalOutputNodeData(UniversalBaseModel):
    label: str
    name: str
    target_handle_id: str
    output_id: str
    output_type: VellumVariableType
    node_input_id: str


class FinalOutputNode(BaseWorkflowNode):
    type: Literal[WorkflowNodeType.TERMINAL] = WorkflowNodeType.TERMINAL
    data: FinalOutputNodeData


WorkflowNode = Union[
    EntrypointNode,
    PromptNode,
    SearchNode,
    FinalOutputNode,
]


class WorkflowEdge(UniversalBaseModel):
    id: str
    source_node_id: str
    source_handle_id: str
    target_node_id: str
    target_handle_id: str


class WorkflowRawData(UniversalBaseModel):
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    display_data: Optional[WorkflowDisplayData] = None


class WorkflowVersionExecConfig(UniversalBaseModel):
    workflow_raw_data: WorkflowRawData
    input_variables: List[VellumVariable]
    output_variables: List[VellumVariable]
