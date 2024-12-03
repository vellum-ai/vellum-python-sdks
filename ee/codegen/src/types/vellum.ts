import { ChatMessage } from "vellum-ai/api";
import {
  ChatMessageRequest,
  ChatMessageRole,
  PromptBlockState,
  PromptParameters,
  SearchResult,
  SearchResultRequest,
  VellumValue,
  VellumVariable,
  VellumVariableType,
} from "vellum-ai/api/types";

export enum WorkflowNodeType {
  PROMPT = "PROMPT",
  TEMPLATING = "TEMPLATING",
  NOTE = "NOTE",
  CODE_EXECUTION = "CODE_EXECUTION",
  METRIC = "METRIC",
  SEARCH = "SEARCH",
  MERGE = "MERGE",
  CONDITIONAL = "CONDITIONAL",
  API = "API",
  ENTRYPOINT = "ENTRYPOINT",
  TERMINAL = "TERMINAL",
  SUBWORKFLOW = "SUBWORKFLOW",
  MAP = "MAP",
  ERROR = "ERROR",
  GENERIC = "GENERIC",
}

export enum ConditionalCombinator {
  OR = "OR",
  AND = "AND",
}

export interface StringVellumValue {
  type: "STRING";
  value: string;
}

export interface NumberVellumValue {
  type: "NUMBER";
  value: number;
}

export interface ChatHistoryVellumValue {
  type: "CHAT_HISTORY";
  value: ChatMessageRequest[] | ChatMessage[];
}

export interface SearchResultsVellumValue {
  type: "SEARCH_RESULTS";
  value: SearchResultRequest[] | SearchResult[];
}

export interface JsonVellumValue {
  type: "JSON";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  value?: any;
}

export interface ConstantValuePointer {
  type: "CONSTANT_VALUE";
  data: VellumValue;
}

export interface NodeOutputData {
  nodeId: string;
  outputId: string;
}

export interface NodeOutputPointer {
  type: "NODE_OUTPUT";
  data: NodeOutputData;
}

export interface InputVariableData {
  inputVariableId: string;
}

export interface InputVariablePointer {
  type: "INPUT_VARIABLE";
  data: InputVariableData;
}

export interface WorkspaceSecretData {
  type: "STRING";
  workspaceSecretId?: string;
}

export interface WorkspaceSecretPointer {
  type: "WORKSPACE_SECRET";
  data: WorkspaceSecretData;
}

export interface ExecutionCounterData {
  nodeId: string;
}

export interface ExecutionCounterPointer {
  type: "EXECUTION_COUNTER";
  data: ExecutionCounterData;
}

export type NodeInputValuePointerRule =
  | NodeOutputPointer
  | InputVariablePointer
  | ConstantValuePointer
  | WorkspaceSecretPointer
  | ExecutionCounterPointer;

export interface NodeInputValuePointer {
  rules: NodeInputValuePointerRule[];
  combinator: "OR";
}

export interface NodeInput {
  id: string;
  key: string;
  value: NodeInputValuePointer;
}

export interface NodeDisplayPosition {
  x: number;
  y: number;
}

export interface NodeDisplayComment {
  value?: string;
  expanded?: boolean;
}

export interface NodeDisplayData {
  position?: NodeDisplayPosition;
  width?: number;
  height?: number;
  comment?: NodeDisplayComment;
}

export interface CodeResourceDefinition {
  name: string;
  module: string[];
}

export interface WorkflowNodeDefinition {
  name: string;
  module: string[];
  bases: CodeResourceDefinition[];
}

export interface BaseWorkflowNode {
  type: string;
  definition?: WorkflowNodeDefinition;
}

export interface BaseDisplayableWorkflowNode extends BaseWorkflowNode {
  id: string;
  inputs: NodeInput[];
  type: string;
  displayData?: NodeDisplayData;
  definition?: WorkflowNodeDefinition;
}

export interface EntrypointNodeData {
  label: string;
  sourceHandleId: string;
}

export interface EntrypointNode extends BaseDisplayableWorkflowNode {
  type: "ENTRYPOINT";
  data: EntrypointNodeData;
}

export interface CacheConfig {
  type: "EPHEMERAL";
}

export interface JinjaPromptTemplateBlock {
  id: string;
  blockType: "JINJA";
  state: PromptBlockState;
  cacheConfig?: CacheConfig;
  properties: {
    template: string;
    templateType?: VellumVariableType;
  };
}

export interface ChatMessagePromptTemplateBlock {
  id: string;
  blockType: "CHAT_MESSAGE";
  state: PromptBlockState;
  cacheConfig?: CacheConfig;
  properties: {
    chatRole: ChatMessageRole;
    chatSource?: string;
    chatMessageUnterminated: boolean;
    blocks: PromptTemplateBlock[];
  };
}

export interface VariablePromptTemplateBlock {
  id: string;
  blockType: "VARIABLE";
  state: PromptBlockState;
  cacheConfig?: CacheConfig;
  inputVariableId: string;
}

export interface PlainTextPromptTemplateBlock {
  id: string;
  blockType: "PLAIN_TEXT";
  state: PromptBlockState;
  cacheConfig?: CacheConfig;
  text: string;
}

export type RichTextChildPromptTemplateBlock =
  | PlainTextPromptTemplateBlock
  | VariablePromptTemplateBlock;

export interface RichTextPromptTemplateBlock {
  id: string;
  blockType: "RICH_TEXT";
  state: PromptBlockState;
  cacheConfig?: CacheConfig;
  blocks: RichTextChildPromptTemplateBlock[];
}

export interface FunctionDefinitionPromptTemplateBlock {
  id: string;
  blockType: "FUNCTION_DEFINITION";
  state: PromptBlockState;
  cacheConfig?: CacheConfig;
  properties: {
    functionName?: string;
    functionDescription?: string;
    functionParameters?: Record<string, unknown>;
    functionForced?: boolean;
    functionStrict?: boolean;
  };
}

export type PromptTemplateBlock =
  | JinjaPromptTemplateBlock
  | ChatMessagePromptTemplateBlock
  | VariablePromptTemplateBlock
  | RichTextPromptTemplateBlock
  | FunctionDefinitionPromptTemplateBlock;

export interface PromptTemplateBlockData {
  version: number;
  blocks: PromptTemplateBlock[];
}

export interface PromptSettings {
  timeout?: number;
}

export interface PromptVersionExecConfig {
  parameters: PromptParameters;
  inputVariables: VellumVariable[];
  promptTemplateBlockData: PromptTemplateBlockData;
  settings?: PromptSettings;
}

export interface BasePromptNodeData {
  label: string;
  outputId: string;
  arrayOutputId: string;
  errorOutputId?: string;
  sourceHandleId: string;
  targetHandleId: string;
}

export interface InlinePromptNodeData extends BasePromptNodeData {
  variant: "INLINE";
  execConfig: PromptVersionExecConfig;
  mlModelName: string;
}

export interface DeploymentPromptNodeData extends BasePromptNodeData {
  variant: "DEPLOYMENT";
  promptDeploymentId: string;
  releaseTag: string;
}

export interface PromptNodeSourceSandbox {
  sandboxId: string;
  promptId: string;
  sandboxSnapshotId: string;
}

export interface PromptVersionData {
  mlModelToWorkspaceId: string;
  execConfig: PromptVersionExecConfig;
}

export interface WorkflowSandboxRoutingConfig {
  version: number;
  promptVersionData?: PromptVersionData;
}

export interface PromptNodeDeployment {
  deploymentId: string;
  deploymentReleaseTagId: string;
}

export interface LegacyPromptNodeData extends BasePromptNodeData {
  variant: "LEGACY";
  sandboxRoutingConfig: WorkflowSandboxRoutingConfig;
  sourceSandbox?: PromptNodeSourceSandbox;
  deployment?: PromptNodeDeployment;
}

export type PromptNodeData =
  | InlinePromptNodeData
  | DeploymentPromptNodeData
  | LegacyPromptNodeData;

export interface InlinePromptNode extends BaseDisplayableWorkflowNode {
  type: "PROMPT";
  data: InlinePromptNodeData;
}

export interface PromptNode extends BaseDisplayableWorkflowNode {
  type: "PROMPT";
  data: PromptNodeData;
}

export interface SearchNodeData {
  label: string;
  resultsOutputId: string;
  textOutputId: string;
  errorOutputId?: string;
  sourceHandleId: string;
  targetHandleId: string;
  queryNodeInputId: string;
  documentIndexNodeInputId: string;
  weightsNodeInputId: string;
  limitNodeInputId: string;
  separatorNodeInputId: string;
  resultMergingEnabledNodeInputId: string;
  externalIdFiltersNodeInputId: string;
  metadataFiltersNodeInputId: string;
}

export interface SearchNode extends BaseDisplayableWorkflowNode {
  type: "SEARCH";
  data: SearchNodeData;
}

export interface DeploymentSubworkflowNodeData {
  label: string;
  sourceHandleId: string;
  targetHandleId: string;
  errorOutputId?: string;
  variant: "DEPLOYMENT";
  workflowDeploymentId: string;
  releaseTag: string;
}
export interface InlineSubworkflowNodeData {
  workflowRawData: WorkflowRawData;
  inputVariables: VellumVariable[];
  outputVariables: VellumVariable[];
  label: string;
  sourceHandleId: string;
  targetHandleId: string;
  errorOutputId?: string;
  variant: "INLINE";
}
export type SubworkflowNodeData =
  | ({
      variant: "DEPLOYMENT";
    } & DeploymentSubworkflowNodeData)
  | ({
      variant: "INLINE";
    } & InlineSubworkflowNodeData);
export interface SubworkflowNode extends BaseDisplayableWorkflowNode {
  type: "SUBWORKFLOW";
  data: SubworkflowNodeData;
}

export interface DeploymentMapNodeData {
  variant: "DEPLOYMENT";
  concurrency?: number;
  label: string;
  sourceHandleId: string;
  targetHandleId: string;
  errorOutputId?: string;
  itemsInputId: string;
  itemInputId: string;
  indexInputId: string;
  workflowDeploymentId: string;
  releaseTag: string;
}
export interface InlineMapNodeData {
  variant: "INLINE";
  workflowRawData: WorkflowRawData;
  inputVariables: VellumVariable[];
  outputVariables: VellumVariable[];
  concurrency?: number;
  label: string;
  sourceHandleId: string;
  targetHandleId: string;
  errorOutputId?: string;
  itemsInputId: string;
  itemInputId: string;
  indexInputId: string;
}
export type MapNodeData =
  | ({
      variant: "DEPLOYMENT";
    } & DeploymentMapNodeData)
  | ({
      variant: "INLINE";
    } & InlineMapNodeData);

export interface MapNode extends BaseDisplayableWorkflowNode {
  type: "MAP";
  data: MapNodeData;
}

export interface GuardrailNodeData {
  label: string;
  sourceHandleId: string;
  targetHandleId: string;
  errorOutputId?: string;
  metricDefinitionId: string;
  releaseTag: string;
}
export interface GuardrailNode extends BaseDisplayableWorkflowNode {
  type: "METRIC";
  data: GuardrailNodeData;
}

export type CodeExecutionPackage = {
  version: string;
  name: string;
};

export interface CodeExecutionNodeData {
  label: string;
  outputId: string;
  errorOutputId?: string;
  logOutputId?: string;
  sourceHandleId: string;
  targetHandleId: string;
  codeInputId: string;
  runtimeInputId: string;
  outputType: VellumVariableType;
  packages?: CodeExecutionPackage[];
  filepath?: string | null;
}
export interface CodeExecutionNode extends BaseDisplayableWorkflowNode {
  type: "CODE_EXECUTION";
  data: CodeExecutionNodeData;
}

export interface TemplatingNodeData {
  label: string;
  outputId: string;
  errorOutputId?: string;
  sourceHandleId: string;
  targetHandleId: string;
  templateNodeInputId: string;
  outputType: VellumVariableType;
}

export interface TemplatingNode extends BaseDisplayableWorkflowNode {
  type: "TEMPLATING";
  data: TemplatingNodeData;
}

export interface ConditionalRuleData {
  id: string;
  rules?: ConditionalRuleData[];
  combinator?: string;
  negated?: boolean;
  fieldNodeInputId?: string;
  operator?: string;
  valueNodeInputId?: string;
}

export interface ConditionalNodeConditionData {
  id: string;
  type: string;
  sourceHandleId: string;
  data?: ConditionalRuleData;
}

export interface ConditionalNodeData {
  label: string;
  targetHandleId: string;
  conditions: ConditionalNodeConditionData[];
  version: string;
}

export interface ConditionalNode extends BaseDisplayableWorkflowNode {
  type: "CONDITIONAL";
  data: ConditionalNodeData;
}

export interface FinalOutputNodeData {
  label: string;
  name: string;
  targetHandleId: string;
  outputId: string;
  outputType: VellumVariableType;
  nodeInputId: string;
}

export interface FinalOutputNode extends BaseDisplayableWorkflowNode {
  type: "TERMINAL";
  data: FinalOutputNodeData;
}

export interface MergeNodeTargetHandle {
  id: string;
}

export interface MergeNodeData {
  label: string;
  mergeStrategy: "AWAIT_ALL" | "AWAIT_ANY";
  targetHandles: MergeNodeTargetHandle[];
  sourceHandleId: string;
}

export interface MergeNode extends BaseDisplayableWorkflowNode {
  type: "MERGE";
  data: MergeNodeData;
}

export interface ApiNodeAdditionalHeaderData {
  headerKeyInputId: string;
  headerValueInputId: string;
}

export interface ApiNodeData {
  label: string;
  methodInputId: string;
  urlInputId: string;
  bodyInputId: string;
  authorizationTypeInputId?: string;
  bearerTokenValueInputId?: string;
  apiKeyHeaderKeyInputId?: string;
  apiKeyHeaderValueInputId?: string;
  additionalHeaders?: ApiNodeAdditionalHeaderData[];
  textOutputId: string;
  jsonOutputId: string;
  statusCodeOutputId: string;
  errorOutputId?: string;
  targetHandleId: string;
  sourceHandleId: string;
}

export interface ApiNode extends BaseDisplayableWorkflowNode {
  type: "API";
  data: ApiNodeData;
}

export interface NoteNodeData {
  label: string;
  text?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  style?: Record<string, any>;
}

export interface NoteNode extends BaseDisplayableWorkflowNode {
  type: "NOTE";
  data: NoteNodeData;
}

export interface ErrorNodeData {
  label: string;
  name: string;
  targetHandleId: string;
  errorSourceInputId: string;
  errorOutputId: string;
  sourceHandleId: string;
}

export interface ErrorNode extends BaseDisplayableWorkflowNode {
  type: "ERROR";
  data: ErrorNodeData;
}

export interface GenericNodeDisplayData {
  position?: { x: number; y: number };
}

export interface GenericNode extends BaseWorkflowNode {
  type: "GENERIC";
  displayData?: GenericNodeDisplayData;
}

export type WorkflowDataNode =
  | PromptNode
  | SearchNode
  | SubworkflowNode
  | TemplatingNode
  | MapNode
  | GuardrailNode
  | CodeExecutionNode
  | FinalOutputNode
  | MergeNode
  | ConditionalNode
  | ApiNode
  | NoteNode
  | ErrorNode
  | GenericNode;

export type WorkflowNode = WorkflowDataNode | EntrypointNode | FinalOutputNode;

export interface WorkflowEdge {
  id: string;
  type: "DEFAULT";
  sourceNodeId: string;
  sourceHandleId: string;
  targetNodeId: string;
  targetHandleId: string;
}

export interface WorkflowDisplayDataViewport {
  x: number;
  y: number;
  zoom: number;
}

export interface WorkflowDisplayData {
  viewport: WorkflowDisplayDataViewport;
}

export interface WorkflowRawData {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  displayData?: WorkflowDisplayData;
  definition?: CodeResourceDefinition;
}

export interface RunnerConfig {
  containerImageName: string;
  containerImageTag: string;
}

export interface WorkflowVersionExecConfig {
  workflowRawData: WorkflowRawData;
  inputVariables: VellumVariable[];
  outputVariables: VellumVariable[];
  runnerConfig?: RunnerConfig;
}
