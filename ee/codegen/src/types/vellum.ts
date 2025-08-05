import { python } from "@fern-api/python-ast";
import {
  ChatMessage,
  ConditionCombinator,
  LogicalOperator,
} from "vellum-ai/api";
import {
  ChatHistoryInput,
  ChatMessageRequest,
  ChatMessageRole,
  FunctionDefinition,
  JsonInput,
  NumberInput,
  PromptBlockState,
  PromptParameters,
  SearchResult,
  SearchResultRequest,
  StringInput,
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

export type VellumLogicalExpression =
  | VellumLogicalCondition
  | VellumLogicalConditionGroup;

export interface VellumLogicalCondition {
  type: "LOGICAL_CONDITION";
  lhsVariableId: string;
  operator: LogicalOperator;
  rhsVariableId: string;
}

export interface VellumLogicalConditionGroup {
  type: "LOGICAL_CONDITION_GROUP";
  conditions: VellumLogicalExpression[];
  combinator: ConditionCombinator;
  negated: boolean;
}

export interface NodeOutputData {
  nodeId: string;
  outputId: string;
}

export interface NodeOutputPointer {
  type: "NODE_OUTPUT";
  data: NodeOutputData;
}

export interface WorkflowOutputPointer {
  type: "NODE_OUTPUT";
  nodeId: string;
  nodeOutputId: string;
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

export interface EnvironmentVariablePointer {
  type: "ENVIRONMENT_VARIABLE";
  data: {
    environmentVariable: string;
  };
}

export type NodeInputValuePointerRule =
  | NodeOutputPointer
  | InputVariablePointer
  | ConstantValuePointer
  | WorkspaceSecretPointer
  | ExecutionCounterPointer
  | EnvironmentVariablePointer;

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

export type MergeBehavior =
  | "AWAIT_ATTRIBUTES"
  | "AWAIT_ALL"
  | "AWAIT_ANY"
  | "CUSTOM";

export interface NodeTrigger {
  id: string;
  mergeBehavior: MergeBehavior;
}

export interface DefaultNodePort {
  type: "DEFAULT";
  id: string;
  name: string;
}

export interface IfConditionNodePort {
  type: "IF";
  id: string;
  name: string;
  expression?: WorkflowValueDescriptor;
}

export interface ElifConditionNodePort {
  type: "ELIF";
  id: string;
  name: string;
  expression?: WorkflowValueDescriptor;
}

export interface ElseConditionNodePort {
  type: "ELSE";
  id: string;
  name: string;
}

export type NodePort =
  | DefaultNodePort
  | IfConditionNodePort
  | ElifConditionNodePort
  | ElseConditionNodePort;

export interface BaseWorkflowNode {
  type: string;
  definition?: CodeResourceDefinition;
}

export interface BaseDisplayableWorkflowNode extends BaseWorkflowNode {
  id: string;
  inputs: NodeInput[];
  type: string;
  displayData?: NodeDisplayData;
  base?: CodeResourceDefinition;
  adornments?: AdornmentNode[];
  outputs?: NodeOutput[];
  attributes?: NodeAttribute[];
  ports?: NodePort[];
  trigger?: NodeTrigger;
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
  type?: "EPHEMERAL";
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
  timeout?: number | null;
  streamEnabled?: boolean | null;
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
  mlModelFallbacks?: string[];
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
  | DeploymentSubworkflowNodeData
  | InlineSubworkflowNodeData;
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
export type MapNodeData = DeploymentMapNodeData | InlineMapNodeData;

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
  repository?: string | null;
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
  name?: string;
  targetHandleId: string;
  errorSourceInputId: string;
  errorOutputId?: string;
}

export interface ErrorNode extends BaseDisplayableWorkflowNode {
  type: "ERROR";
  data: ErrorNodeData;
}

export interface GenericNodeDisplayData {
  position?: { x: number; y: number };
}

export interface NodeOutput {
  id: string;
  name: string;
  type: VellumVariableType;
  value?: WorkflowValueDescriptor;
}

export interface GenericNode extends BaseWorkflowNode {
  id: string;
  label: string;
  type: "GENERIC";
  displayData?: GenericNodeDisplayData;
  base: CodeResourceDefinition;
  definition?: CodeResourceDefinition;
  trigger: NodeTrigger;
  ports: NodePort[];
  adornments?: AdornmentNode[];
  attributes: NodeAttribute[];
  outputs: NodeOutput[];
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

export interface WorkflowOutputValue {
  outputVariableId: string;
  value?: WorkflowValueDescriptor;
}

export interface WorkflowRawData {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  displayData?: WorkflowDisplayData;
  definition?: CodeResourceDefinition;
  outputValues?: WorkflowOutputValue[];
}

export interface RunnerConfig {
  containerImageName?: string;
  containerImageTag?: string;
}

export interface ModuleData {
  additionalFiles?: Record<string, string>;
}

export interface WorkflowVersionExecConfig {
  workflowRawData: WorkflowRawData;
  inputVariables: VellumVariable[];
  stateVariables?: VellumVariable[];
  outputVariables: VellumVariable[];
  runnerConfig?: RunnerConfig;
  moduleData?: ModuleData;
}

type WorkflowSandboxInput =
  | StringInput
  | JsonInput
  | ChatHistoryInput
  | NumberInput;
export type WorkflowSandboxInputs = WorkflowSandboxInput[];

export interface UnaryWorkflowExpression {
  type: "UNARY_EXPRESSION";
  lhs?: WorkflowValueDescriptor;
  operator: LogicalOperator;
}

export interface BinaryWorkflowExpression {
  type: "BINARY_EXPRESSION";
  lhs?: WorkflowValueDescriptor;
  operator: LogicalOperator;
  rhs?: WorkflowValueDescriptor;
}

export interface TernaryWorkflowExpression {
  type: "TERNARY_EXPRESSION";
  base?: WorkflowValueDescriptor;
  operator: LogicalOperator;
  lhs?: WorkflowValueDescriptor;
  rhs?: WorkflowValueDescriptor;
}

export interface NodeOutputWorkflowReference {
  type: "NODE_OUTPUT";
  nodeId: string;
  nodeOutputId: string;
}

export interface WorkflowInputWorkflowReference {
  type: "WORKFLOW_INPUT";
  inputVariableId: string;
}

export interface WorkflowStateVariableWorkflowReference {
  type: "WORKFLOW_STATE";
  stateVariableId: string;
}

export interface ConstantValueWorkflowReference {
  type: "CONSTANT_VALUE";
  value: VellumValue;
}

export interface VellumSecretWorkflowReference {
  type: "VELLUM_SECRET";
  vellumSecretName: string;
}

export interface EnvironmentVariableWorkflowReference {
  type: "ENVIRONMENT_VARIABLE";
  environmentVariable: string;
}

export interface ExecutionCounterWorkflowReference {
  type: "EXECUTION_COUNTER";
  nodeId: string;
}

export interface DictionaryWorkflowReferenceEntry {
  id?: string; // TODO: Temporary supporting id key translation for input variable in blocks
  key: string;
  value: WorkflowValueDescriptor | null;
}

export interface DictionaryWorkflowReference {
  type: "DICTIONARY_REFERENCE";
  entries: DictionaryWorkflowReferenceEntry[];
}

export interface ArrayWorkflowReference {
  type: "ARRAY_REFERENCE";
  items: WorkflowValueDescriptor[];
}

export type WorkflowExpression =
  | UnaryWorkflowExpression
  | BinaryWorkflowExpression
  | TernaryWorkflowExpression;

export type WorkflowValueDescriptorReference =
  | NodeOutputWorkflowReference
  | WorkflowInputWorkflowReference
  | WorkflowStateVariableWorkflowReference
  | ConstantValueWorkflowReference
  | VellumSecretWorkflowReference
  | EnvironmentVariableWorkflowReference
  | ExecutionCounterWorkflowReference
  | DictionaryWorkflowReference
  | ArrayWorkflowReference;

export type WorkflowValueDescriptor =
  | WorkflowExpression
  | WorkflowValueDescriptorReference;

export interface NodeAttribute {
  id: string;
  name: string;
  value?: WorkflowValueDescriptor | null;
}

export interface AdornmentNode {
  id: string;
  label: string;
  base: CodeResourceDefinition;
  attributes: NodeAttribute[];
}

export type OperatorMapping =
  | "equals"
  | "does_not_equal"
  | "less_than"
  | "greater_than"
  | "less_than_or_equal_to"
  | "greater_than_or_equal_to"
  | "contains"
  | "begins_with"
  | "ends_with"
  | "does_not_contain"
  | "does_not_begin_with"
  | "does_not_end_with"
  | "is_null"
  | "is_not_null"
  | "in"
  | "not_in"
  | "between"
  | "not_between"
  | "is_blank"
  | "is_not_blank"
  | "parse_json"
  | "coalesce"
  | "access_field"
  | "or"
  | "and"
  | "is_error";

export interface IterableConfig {
  endWithComma?: boolean;
}

export interface AttributeConfig {
  lhs: python.Reference;
}

interface NameDescription {
  name: string;
  description: string;
}

export type FunctionArgs = {
  type: "CODE_EXECUTION";
  src: string;
  definition: FunctionDefinition;
} & NameDescription;

export type InlineWorkflowFunctionArgs = {
  type: "INLINE_WORKFLOW";
  exec_config: WorkflowVersionExecConfig;
} & NameDescription;

export type WorkflowDeploymentFunctionArgs = {
  type: "WORKFLOW_DEPLOYMENT";
  deployment: string;
  release_tag: string | null;
} & NameDescription;

export type ComposioToolFunctionArgs = {
  type: "COMPOSIO";
  toolkit?: string;
  action?: string;
  description: string;
  tool_name?: string;
  tool_slug?: string;
  connection_id?: string;
  integration_name?: string;
  user_id?: string | null;
} & NameDescription;

export type MCPServerFunctionArgs = {
  type: "MCP_SERVER";
  name: WorkflowValueDescriptor;
  url: WorkflowValueDescriptor;
  authorization_type: WorkflowValueDescriptor;
  bearer_token_value?: WorkflowValueDescriptor;
  api_key_header_key?: WorkflowValueDescriptor;
  api_key_header_value?: WorkflowValueDescriptor;
};

export type ToolArgs = (
  | FunctionArgs
  | InlineWorkflowFunctionArgs
  | WorkflowDeploymentFunctionArgs
  | ComposioToolFunctionArgs
  | MCPServerFunctionArgs
)[];
