import { ChatMessageRole, PromptBlockState } from "vellum-ai/api";
import {
  object as objectSchema,
  list as listSchema,
  undiscriminatedUnion as undiscriminatedUnionSchema,
  string as stringSchema,
  stringLiteral as stringLiteralSchema,
  number as numberSchema,
  any as anySchema,
  boolean as booleanSchema,
  ObjectSchema,
  lazy,
  property as propertySchema,
  Schema,
  record as recordSchema,
  unknown as unknownSchema,
} from "vellum-ai/core/schemas";
import {
  ChatMessageRole as ChatMessageRoleSerializer,
  VellumVariable as VellumVariableSerializer,
  VellumVariableType as VellumVariableTypeSerializer,
  PromptBlockState as PromptBlockStateSerializer,
  PromptParameters as PromptParametersSerializer,
  VellumValue as VellumValueSerializer,
} from "vellum-ai/serialization";

import {
  ApiNode,
  ApiNodeAdditionalHeaderData,
  CodeExecutionNode,
  CodeExecutionNodeData,
  CodeExecutionPackage,
  CodeResourceDefinition,
  ConditionalNode,
  ConditionalNodeConditionData,
  ConditionalNodeData,
  ConditionalRuleData,
  ConstantValuePointer,
  DeploymentMapNodeData,
  DeploymentPromptNodeData,
  DeploymentSubworkflowNodeData,
  EntrypointNode,
  GuardrailNode,
  InlineMapNodeData,
  InlinePromptNodeData,
  InlineSubworkflowNodeData,
  InputVariablePointer,
  MapNode,
  MapNodeData,
  NodeDisplayComment,
  NodeDisplayData,
  NodeDisplayPosition,
  NodeInput,
  NodeInputValuePointerRule,
  NodeOutputPointer,
  PromptNode,
  PromptNodeData,
  PromptSettings,
  PromptVersionExecConfig,
  SearchNode,
  SearchNodeData,
  SubworkflowNode,
  TemplatingNode,
  FinalOutputNode,
  WorkflowDisplayData,
  WorkflowDisplayDataViewport,
  WorkflowEdge,
  WorkflowNode,
  WorkflowNodeDefinition,
  WorkflowRawData,
  WorkflowVersionExecConfig,
  WorkspaceSecretPointer,
  MergeNode,
  MergeNodeTargetHandle,
  NoteNode,
  ErrorNode,
  PromptNodeSourceSandbox,
  WorkflowSandboxRoutingConfig,
  PromptNodeDeployment,
  PromptVersionData,
  LegacyPromptNodeData,
  GenericNode,
  ExecutionCounterPointer,
  GenericNodeDisplayData,
  JinjaPromptTemplateBlock,
  VariablePromptTemplateBlock,
  ChatMessagePromptTemplateBlock,
  RichTextPromptTemplateBlock,
  PlainTextPromptTemplateBlock,
  FunctionDefinitionPromptTemplateBlock,
} from "src/types/vellum";

const CacheConfigSerializer = objectSchema({
  type: stringLiteralSchema("EPHEMERAL"),
});

export const JinjaPromptTemplateBlockSerializer: ObjectSchema<
  JinjaPromptTemplateBlockSerializer.Raw,
  JinjaPromptTemplateBlock
> = objectSchema({
  id: stringSchema(),
  blockType: propertySchema("block_type", stringLiteralSchema("JINJA")),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  properties: objectSchema({
    template: stringSchema(),
    templateType: propertySchema(
      "template_type",
      VellumVariableTypeSerializer.optional()
    ),
  }),
});

export declare namespace JinjaPromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    block_type: "JINJA";
    state: PromptBlockState;
    cache_config?: { type: "EPHEMERAL" } | null;
    properties: {
      template?: string | null;
      template_type?: string | null;
    };
  }
}

export const ChatMessagePromptTemplateBlockSerializer: ObjectSchema<
  ChatMessagePromptTemplateBlockSerializer.Raw,
  ChatMessagePromptTemplateBlock
> = objectSchema({
  id: stringSchema(),
  blockType: propertySchema("block_type", stringLiteralSchema("CHAT_MESSAGE")),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  properties: objectSchema({
    chatRole: propertySchema("chat_role", ChatMessageRoleSerializer),
    chatSource: propertySchema("chat_source", stringSchema().optional()),
    chatMessageUnterminated: propertySchema(
      "chat_message_unterminated",
      booleanSchema()
    ),
    blocks: propertySchema(
      "blocks",
      listSchema(lazy(() => PromptTemplateBlockSerializer))
    ),
  }),
});

export declare namespace ChatMessagePromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    block_type: "CHAT_MESSAGE";
    state: PromptBlockState;
    cache_config?: { type: "EPHEMERAL" } | null;
    properties: {
      chat_role?: ChatMessageRole | null;
      chat_source?: string | null;
      chat_message_unterminated: boolean;
      blocks: PromptTemplateBlockSerializer.Raw[];
    };
  }
}

export const VariablePromptTemplateBlockSerializer: ObjectSchema<
  VariablePromptTemplateBlockSerializer.Raw,
  VariablePromptTemplateBlock
> = objectSchema({
  id: stringSchema(),
  blockType: propertySchema("block_type", stringLiteralSchema("VARIABLE")),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  inputVariableId: propertySchema("input_variable_id", stringSchema()),
});

export declare namespace VariablePromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    block_type: "VARIABLE";
    state: PromptBlockState;
    cache_config?: { type: "EPHEMERAL" } | null;
    input_variable_id: string;
  }
}

export const PlainTextPromptTemplateBlockSerializer: ObjectSchema<
  PlainTextPromptTemplateBlockSerializer.Raw,
  PlainTextPromptTemplateBlock
> = objectSchema({
  id: stringSchema(),
  blockType: propertySchema("block_type", stringLiteralSchema("PLAIN_TEXT")),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  text: stringSchema(),
});

export declare namespace PlainTextPromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    block_type: "PLAIN_TEXT";
    state: PromptBlockState;
    cache_config?: { type: "EPHEMERAL" } | null;
    text: string;
  }
}

export const RichTextPromptTemplateBlockSerializer: ObjectSchema<
  RichTextPromptTemplateBlockSerializer.Raw,
  RichTextPromptTemplateBlock
> = objectSchema({
  id: stringSchema(),
  blockType: propertySchema("block_type", stringLiteralSchema("RICH_TEXT")),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  blocks: listSchema(
    undiscriminatedUnionSchema([
      PlainTextPromptTemplateBlockSerializer,
      VariablePromptTemplateBlockSerializer,
    ])
  ),
});

export declare namespace RichTextPromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    block_type: "RICH_TEXT";
    state: PromptBlockState;
    cache_config?: { type: "EPHEMERAL" } | null;
    blocks: Array<
      | PlainTextPromptTemplateBlockSerializer.Raw
      | VariablePromptTemplateBlockSerializer.Raw
    >;
  }
}

export const FunctionDefinitionPromptTemplateBlockSerializer: ObjectSchema<
  FunctionDefinitionPromptTemplateBlockSerializer.Raw,
  FunctionDefinitionPromptTemplateBlock
> = objectSchema({
  id: stringSchema(),
  blockType: propertySchema(
    "block_type",
    stringLiteralSchema("FUNCTION_DEFINITION")
  ),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  properties: objectSchema({
    functionName: propertySchema("function_name", stringSchema().optional()),
    functionDescription: propertySchema(
      "function_description",
      stringSchema().optional()
    ),
    functionParameters: propertySchema(
      "function_parameters",
      recordSchema(stringSchema(), unknownSchema()).optional()
    ),
    functionForced: propertySchema(
      "function_forced",
      booleanSchema().optional()
    ),
    functionStrict: propertySchema(
      "function_strict",
      booleanSchema().optional()
    ),
  }),
});

export declare namespace FunctionDefinitionPromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    block_type: "FUNCTION_DEFINITION";
    state: PromptBlockState;
    cache_config?: { type: "EPHEMERAL" } | null;
    properties: {
      function_name?: string | null;
      function_description?: string | null;
      function_parameters?: Record<string, unknown> | null;
      function_forced?: boolean | null;
      function_strict?: boolean | null;
    };
  }
}

export declare namespace PromptTemplateBlockSerializer {
  type Raw =
    | JinjaPromptTemplateBlockSerializer.Raw
    | ChatMessagePromptTemplateBlockSerializer.Raw
    | VariablePromptTemplateBlockSerializer.Raw
    | RichTextPromptTemplateBlockSerializer.Raw
    | FunctionDefinitionPromptTemplateBlockSerializer.Raw;
}

const PromptTemplateBlockSerializer = undiscriminatedUnionSchema([
  JinjaPromptTemplateBlockSerializer,
  ChatMessagePromptTemplateBlockSerializer,
  VariablePromptTemplateBlockSerializer,
  RichTextPromptTemplateBlockSerializer,
  FunctionDefinitionPromptTemplateBlockSerializer,
]);

export const NodeOutputPointerSerializer: ObjectSchema<
  NodeOutputPointerSerializer.Raw,
  NodeOutputPointer
> = objectSchema({
  type: stringLiteralSchema("NODE_OUTPUT"),
  data: objectSchema({
    nodeId: propertySchema("node_id", stringSchema()),
    outputId: propertySchema("output_id", stringSchema()),
  }),
});

export declare namespace NodeOutputPointerSerializer {
  interface Raw {
    type: "NODE_OUTPUT";
    data: {
      node_id: string;
    };
  }
}

export const InputVariablePointerSerializer: ObjectSchema<
  InputVariablePointerSerializer.Raw,
  InputVariablePointer
> = objectSchema({
  type: stringLiteralSchema("INPUT_VARIABLE"),
  data: objectSchema({
    inputVariableId: propertySchema("input_variable_id", stringSchema()),
  }),
});

export declare namespace InputVariablePointerSerializer {
  interface Raw {
    type: "INPUT_VARIABLE";
    data: {
      input_variable_id: string;
    };
  }
}

export const ConstantValuePointerSerializer: ObjectSchema<
  ConstantValuePointerSerializer.Raw,
  ConstantValuePointer
> = objectSchema({
  type: stringLiteralSchema("CONSTANT_VALUE"),
  data: VellumValueSerializer,
});

export declare namespace ConstantValuePointerSerializer {
  interface Raw {
    type: "CONSTANT_VALUE";
    data: VellumValueSerializer.Raw;
  }
}

export const WorkspaceSecretPointerSerializer: ObjectSchema<
  WorkspaceSecretPointerSerializer.Raw,
  WorkspaceSecretPointer
> = objectSchema({
  type: stringLiteralSchema("WORKSPACE_SECRET"),
  data: objectSchema({
    type: stringLiteralSchema("STRING"),
    workspaceSecretId: propertySchema(
      "workspace_secret_id",
      stringSchema().optional()
    ),
  }),
});

export declare namespace WorkspaceSecretPointerSerializer {
  interface Raw {
    type: "WORKSPACE_SECRET";
    data: {
      type: "STRING";
      workspace_secret_id?: string | null | undefined;
    };
  }
}

export const ExecutionCounterPointerSerializer: ObjectSchema<
  ExecutionCounterPointerSerializer.Raw,
  ExecutionCounterPointer
> = objectSchema({
  type: stringLiteralSchema("EXECUTION_COUNTER"),
  data: objectSchema({
    nodeId: propertySchema("node_id", stringSchema()),
  }),
});

export declare namespace ExecutionCounterPointerSerializer {
  interface Raw {
    type: "EXECUTION_COUNTER";
    data: {
      node_id: string;
    };
  }
}

export const NodeInputValuePointerRuleSerializer: Schema<
  NodeInputValuePointerRuleSerializer.Raw,
  NodeInputValuePointerRule
> = undiscriminatedUnionSchema([
  NodeOutputPointerSerializer,
  InputVariablePointerSerializer,
  ConstantValuePointerSerializer,
  WorkspaceSecretPointerSerializer,
  ExecutionCounterPointerSerializer,
]);

export declare namespace NodeInputValuePointerRuleSerializer {
  type Raw =
    | NodeOutputPointerSerializer.Raw
    | InputVariablePointerSerializer.Raw
    | ConstantValuePointerSerializer.Raw
    | WorkspaceSecretPointerSerializer.Raw
    | ExecutionCounterPointerSerializer.Raw;
}

export const NodeInputSerializer: ObjectSchema<
  NodeInputSerializer.Raw,
  NodeInput
> = objectSchema({
  id: stringSchema(),
  key: stringSchema(),
  value: objectSchema({
    rules: listSchema(NodeInputValuePointerRuleSerializer),
    combinator: stringLiteralSchema("OR"),
  }),
});

export declare namespace NodeInputSerializer {
  interface Raw {
    id: string;
    key: string;
    value: {
      rules: NodeInputValuePointerRuleSerializer.Raw[];
      combinator: "OR";
    };
  }
}

export const CodeResourceDefinitionSerializer: ObjectSchema<
  CodeResourceDefinitionSerializer.Raw,
  CodeResourceDefinition
> = objectSchema({
  name: stringSchema(),
  module: listSchema(stringSchema()),
});

export declare namespace CodeResourceDefinitionSerializer {
  interface Raw {
    name: string;
    module: string[];
  }
}

export const WorkflowNodeDefinitionSerializer: ObjectSchema<
  WorkflowNodeDefinitionSerializer.Raw,
  WorkflowNodeDefinition
> = objectSchema({
  name: stringSchema(),
  module: listSchema(stringSchema()),
  bases: listSchema(CodeResourceDefinitionSerializer),
});

export declare namespace WorkflowNodeDefinitionSerializer {
  interface Raw {
    name: string;
    module: string[];
    bases: CodeResourceDefinitionSerializer.Raw[];
  }
}

export const PromptTemplateBlockDataSerializer = objectSchema({
  version: numberSchema(),
  blocks: listSchema(PromptTemplateBlockSerializer),
});

export declare namespace PromptTemplateBlockDataSerializer {
  interface Raw {
    version: number;
    blocks: PromptTemplateBlockSerializer.Raw[];
  }
}

const PromptSettingsSerializer: ObjectSchema<
  PromptSettingsSerializer.Raw,
  PromptSettings
> = objectSchema({
  timeout: numberSchema().optional(),
});

export declare namespace PromptSettingsSerializer {
  interface Raw {
    timeout?: number | null;
  }
}

export const PromptVersionExecConfigSerializer: Schema<
  PromptVersionExecConfigSerializer.Raw,
  PromptVersionExecConfig
> = objectSchema({
  parameters: propertySchema("parameters", PromptParametersSerializer),
  inputVariables: propertySchema(
    "input_variables",
    listSchema(VellumVariableSerializer)
  ),
  promptTemplateBlockData: propertySchema(
    "prompt_template_block_data",
    PromptTemplateBlockDataSerializer
  ),
  settings: PromptSettingsSerializer.optional(),
});

export declare namespace PromptVersionExecConfigSerializer {
  interface Raw {
    parameters: PromptParametersSerializer.Raw;
    input_variables: VellumVariableSerializer.Raw[];
    prompt_template_block_data: PromptTemplateBlockDataSerializer.Raw;
    settings?: PromptSettingsSerializer.Raw | null;
  }
}

export const NodeDisplayCommentSerializer: ObjectSchema<
  NodeDisplayCommentSerializer.Raw,
  NodeDisplayComment
> = objectSchema({
  value: stringSchema().optional(),
  expanded: booleanSchema().optional(),
});

export declare namespace NodeDisplayCommentSerializer {
  interface Raw {
    value?: string | null;
    expanded?: boolean | null;
  }
}

export const NodeDisplayPositionSerializer: ObjectSchema<
  NodeDisplayPositionSerializer.Raw,
  NodeDisplayPosition
> = objectSchema({
  x: numberSchema(),
  y: numberSchema(),
});

export declare namespace NodeDisplayPositionSerializer {
  interface Raw {
    x: number;
    y: number;
  }
}

export const NodeDisplayDataSerializer: ObjectSchema<
  NodeDisplayDataSerializer.Raw,
  NodeDisplayData
> = objectSchema({
  position: NodeDisplayPositionSerializer.optional(),
  width: numberSchema().optional(),
  height: numberSchema().optional(),
  comment: NodeDisplayCommentSerializer.optional(),
});

export declare namespace NodeDisplayDataSerializer {
  interface Raw {
    position?: NodeDisplayPositionSerializer.Raw | null;
    width?: number | null;
    height?: number | null;
    comment?: NodeDisplayCommentSerializer.Raw | null;
  }
}

export declare namespace BaseWorkflowNodeSerializer {
  interface Raw {
    type: string;
    definition?: WorkflowNodeDefinitionSerializer.Raw | null;
  }
}

export declare namespace BaseDisplayableWorkflowNodeSerializer {
  interface Raw extends BaseWorkflowNodeSerializer.Raw {
    id: string;
    display_data?: NodeDisplayDataSerializer.Raw | null;
    inputs: NodeInputSerializer.Raw[];
  }
}

export const EntrypointNodeSerializer: ObjectSchema<
  EntrypointNodeSerializer.Raw,
  EntrypointNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("ENTRYPOINT"),
  data: objectSchema({
    label: stringSchema(),
    sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace EntrypointNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "ENTRYPOINT";
    data: {
      label: string;
      source_handle_id: string;
    };
  }
}

export const InlineSubworkflowNodeDataSerializer: ObjectSchema<
  InlineSubworkflowNodeDataSerializer.Raw,
  InlineSubworkflowNodeData
> = objectSchema({
  workflowRawData: propertySchema(
    "workflow_raw_data",
    lazy(() => WorkflowRawDataSerializer)
  ),
  inputVariables: propertySchema(
    "input_variables",
    listSchema(VellumVariableSerializer)
  ),
  outputVariables: propertySchema(
    "output_variables",
    listSchema(VellumVariableSerializer)
  ),
  label: stringSchema(),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  variant: stringLiteralSchema("INLINE"),
});

export declare namespace InlineSubworkflowNodeDataSerializer {
  interface Raw {
    workflow_raw_data: WorkflowRawDataSerializer.Raw;
    input_variables: VellumVariableSerializer.Raw[];
    output_variables: VellumVariableSerializer.Raw[];
    label: string;
    source_handle_id: string;
    target_handle_id: string;
    error_output_id?: string | null;
    variant: "INLINE";
  }
}

export const DeploymentSubworkflowNodeDataSerializer: ObjectSchema<
  DeploymentSubworkflowNodeDataSerializer.Raw,
  DeploymentSubworkflowNodeData
> = objectSchema({
  label: stringSchema(),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  variant: stringLiteralSchema("DEPLOYMENT"),
  workflowDeploymentId: propertySchema(
    "workflow_deployment_id",
    stringSchema()
  ),
  releaseTag: propertySchema("release_tag", stringSchema()),
});

export declare namespace DeploymentSubworkflowNodeDataSerializer {
  interface Raw {
    label: string;
    source_handle_id: string;
    target_handle_id: string;
    error_output_id?: string | null;
    variant: "DEPLOYMENT";
    workflow_deployment_id: string;
    release_tag: string;
  }
}

export const SubworkflowNodeDataSerializer = undiscriminatedUnionSchema([
  InlineSubworkflowNodeDataSerializer,
  DeploymentSubworkflowNodeDataSerializer,
]);

export declare namespace SubworkflowNodeDataSerializer {
  type Raw =
    | InlineSubworkflowNodeDataSerializer.Raw
    | DeploymentSubworkflowNodeDataSerializer.Raw;
}

export const SubworkflowNodeSerializer: ObjectSchema<
  SubworkflowNodeSerializer.Raw,
  SubworkflowNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("SUBWORKFLOW"),
  data: SubworkflowNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace SubworkflowNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "SUBWORKFLOW";
    data: SubworkflowNodeDataSerializer.Raw;
  }
}

export const InlinePromptNodeDataSerializer: ObjectSchema<
  InlinePromptNodeDataSerializer.Raw,
  InlinePromptNodeData
> = objectSchema({
  label: stringSchema(),
  variant: stringLiteralSchema("INLINE"),
  outputId: propertySchema("output_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  arrayOutputId: propertySchema("array_output_id", stringSchema()),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  execConfig: propertySchema("exec_config", PromptVersionExecConfigSerializer),
  mlModelName: propertySchema("ml_model_name", stringSchema()),
});

export declare namespace InlinePromptNodeDataSerializer {
  interface Raw {
    label: string;
    output_id: string;
    error_output_id?: string | null;
    array_output_id: string;
    source_handle_id: string;
    target_handle_id: string;
    variant: "INLINE";
    exec_config: PromptVersionExecConfigSerializer.Raw;
    ml_model_name: string;
  }
}

export const DeploymentPromptNodeDataSerializer: ObjectSchema<
  DeploymentPromptNodeDataSerializer.Raw,
  DeploymentPromptNodeData
> = objectSchema({
  label: stringSchema(),
  variant: stringLiteralSchema("DEPLOYMENT"),
  promptDeploymentId: propertySchema("prompt_deployment_id", stringSchema()),
  releaseTag: propertySchema("release_tag", stringSchema()),
  outputId: propertySchema("output_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  arrayOutputId: propertySchema("array_output_id", stringSchema()),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
});

export declare namespace DeploymentPromptNodeDataSerializer {
  interface Raw {
    variant: "DEPLOYMENT";
    prompt_deployment_id: string;
    release_tag: string;
    label: string;
    output_id: string;
    error_output_id?: string | null;
    array_output_id: string;
    source_handle_id: string;
    target_handle_id: string;
  }
}

export const PromptVersionDataSerializer: ObjectSchema<
  PromptVersionDataSerializer.Raw,
  PromptVersionData
> = objectSchema({
  mlModelToWorkspaceId: propertySchema(
    "ml_model_to_workspace_id",
    stringSchema()
  ),
  execConfig: propertySchema("exec_config", PromptVersionExecConfigSerializer),
});

export declare namespace PromptVersionDataSerializer {
  interface Raw {
    ml_model_to_workspace_id: string;
    exec_config: PromptVersionExecConfigSerializer.Raw;
  }
}

export const PromptNodeSourceSandboxSerializer: ObjectSchema<
  PromptNodeSourceSandboxSerializer.Raw,
  PromptNodeSourceSandbox
> = objectSchema({
  sandboxId: propertySchema("sandbox_id", stringSchema()),
  promptId: propertySchema("prompt_id", stringSchema()),
  sandboxSnapshotId: propertySchema("sandbox_snapshot_id", stringSchema()),
});

export declare namespace PromptNodeSourceSandboxSerializer {
  interface Raw {
    sandbox_id: string;
    prompt_id: string;
    sandbox_snapshot_id: string;
  }
}

export const WorkflowSandboxRoutingConfigSerializer: ObjectSchema<
  WorkflowSandboxRoutingConfigSerializer.Raw,
  WorkflowSandboxRoutingConfig
> = objectSchema({
  version: numberSchema(),
  promptVersionData: propertySchema(
    "prompt_version_data",
    PromptVersionDataSerializer.optional()
  ),
});

export declare namespace WorkflowSandboxRoutingConfigSerializer {
  interface Raw {
    version: number;
    prompt_version_data?: PromptVersionDataSerializer.Raw | null;
  }
}

export const PromptNodeDeploymentSerializer: ObjectSchema<
  PromptNodeDeploymentSerializer.Raw,
  PromptNodeDeployment
> = objectSchema({
  deploymentId: propertySchema("deployment_id", stringSchema()),
  deploymentReleaseTagId: propertySchema(
    "deployment_release_tag_id",
    stringSchema()
  ),
});

export declare namespace PromptNodeDeploymentSerializer {
  interface Raw {
    deployment_id: string;
    deployment_release_tag_id: string;
  }
}

export const LegacyPromptNodeDataSerializer: ObjectSchema<
  LegacyPromptNodeDataSerializer.Raw,
  LegacyPromptNodeData
> = objectSchema({
  label: stringSchema(),
  variant: stringLiteralSchema("LEGACY"),
  outputId: propertySchema("output_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  arrayOutputId: propertySchema("array_output_id", stringSchema()),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  sandboxRoutingConfig: propertySchema(
    "sandbox_routing_config",
    WorkflowSandboxRoutingConfigSerializer
  ),
  sourceSandbox: propertySchema(
    "source_sandbox",
    PromptNodeSourceSandboxSerializer.optional()
  ),
  deployment: PromptNodeDeploymentSerializer.optional(),
});

export declare namespace LegacyPromptNodeDataSerializer {
  interface Raw {
    label: string;
    variant: "LEGACY";
    output_id: string;
    error_output_id?: string | null;
    array_output_id: string;
    source_handle_id: string;
    target_handle_id: string;
    sandbox_routing_config: WorkflowSandboxRoutingConfigSerializer.Raw;
    source_sandbox?: PromptNodeSourceSandboxSerializer.Raw | null;
    deployment?: PromptNodeDeploymentSerializer.Raw | null;
  }
}

export const PromptNodeDataSerializer: Schema<
  PromptNodeDataSerializer.Raw,
  PromptNodeData
> = undiscriminatedUnionSchema([
  InlinePromptNodeDataSerializer,
  DeploymentPromptNodeDataSerializer,
  LegacyPromptNodeDataSerializer,
]);

export declare namespace PromptNodeDataSerializer {
  type Raw =
    | InlinePromptNodeDataSerializer.Raw
    | DeploymentPromptNodeDataSerializer.Raw
    | LegacyPromptNodeDataSerializer.Raw;
}

export const PromptNodeSerializer: ObjectSchema<
  PromptNodeSerializer.Raw,
  PromptNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("PROMPT"),
  data: PromptNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace PromptNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "PROMPT";
    data: PromptNodeDataSerializer.Raw;
  }
}

export const DeploymentMapNodeDataSerializer: ObjectSchema<
  DeploymentMapNodeDataSerializer.Raw,
  DeploymentMapNodeData
> = objectSchema({
  variant: stringLiteralSchema("DEPLOYMENT"),
  concurrency: numberSchema().optional(),
  label: stringSchema(),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  itemsInputId: propertySchema("items_input_id", stringSchema()),
  itemInputId: propertySchema("item_input_id", stringSchema()),
  indexInputId: propertySchema("index_input_id", stringSchema()),
  workflowDeploymentId: propertySchema(
    "workflow_deployment_id",
    stringSchema()
  ),
  releaseTag: propertySchema("release_tag", stringSchema()),
});

export declare namespace DeploymentMapNodeDataSerializer {
  interface Raw {
    variant: "DEPLOYMENT";
    concurrency?: number | null;
    label: string;
    source_handle_id: string;
    target_handle_id: string;
    error_output_id?: string | null;
    items_input_id: string;
    item_input_id: string;
    index_input_id: string;
    workflow_deployment_id: string;
    release_tag: string;
  }
}

export const InlineMapNodeDataSerializer: ObjectSchema<
  InlineMapNodeDataSerializer.Raw,
  InlineMapNodeData
> = objectSchema({
  variant: stringLiteralSchema("INLINE"),
  workflowRawData: propertySchema(
    "workflow_raw_data",
    lazy(() => WorkflowRawDataSerializer)
  ),
  inputVariables: propertySchema(
    "input_variables",
    listSchema(VellumVariableSerializer)
  ),
  outputVariables: propertySchema(
    "output_variables",
    listSchema(VellumVariableSerializer)
  ),
  concurrency: numberSchema().optional(),
  label: stringSchema(),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  itemsInputId: propertySchema("items_input_id", stringSchema()),
  itemInputId: propertySchema("item_input_id", stringSchema()),
  indexInputId: propertySchema("index_input_id", stringSchema()),
});

export declare namespace InlineMapNodeDataSerializer {
  interface Raw {
    variant: "INLINE";
    workflow_raw_data: WorkflowRawDataSerializer.Raw;
    input_variables: VellumVariableSerializer.Raw[];
    output_variables: VellumVariableSerializer.Raw[];
    concurrency?: number | null;
    label: string;
    source_handle_id: string;
    target_handle_id: string;
    error_output_id?: string | null;
    items_input_id: string;
    item_input_id: string;
    index_input_id: string;
  }
}

export const MapNodeDataSerializer: Schema<
  MapNodeDataSerializer.Raw,
  MapNodeData
> = undiscriminatedUnionSchema([
  InlineMapNodeDataSerializer,
  DeploymentMapNodeDataSerializer,
]);

export declare namespace MapNodeDataSerializer {
  type Raw =
    | InlineMapNodeDataSerializer.Raw
    | DeploymentMapNodeDataSerializer.Raw;
}

export const MapNodeSerializer: ObjectSchema<MapNodeSerializer.Raw, MapNode> =
  objectSchema({
    id: stringSchema(),
    type: stringLiteralSchema("MAP"),
    data: MapNodeDataSerializer,
    inputs: listSchema(NodeInputSerializer),
    displayData: propertySchema(
      "display_data",
      NodeDisplayDataSerializer.optional()
    ),
    definition: WorkflowNodeDefinitionSerializer.optional(),
  });

export declare namespace MapNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "MAP";
    data: MapNodeDataSerializer.Raw;
  }
}

export const GuardrailNodeSerializer: ObjectSchema<
  GuardrailNodeSerializer.Raw,
  GuardrailNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("METRIC"),
  data: objectSchema({
    label: stringSchema(),
    sourceHandleId: propertySchema("source_handle_id", stringSchema()),
    targetHandleId: propertySchema("target_handle_id", stringSchema()),
    errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
    metricDefinitionId: propertySchema("metric_definition_id", stringSchema()),
    releaseTag: propertySchema("release_tag", stringSchema()),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace GuardrailNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "METRIC";
    data: {
      label: string;
      source_handle_id: string;
      target_handle_id: string;
      error_output_id?: string | null;
      metric_definition_id: string;
      release_tag: string;
    };
  }
}

export const CodeExecutionPackageSerializer: ObjectSchema<
  CodeExecutionPackageSerializer.Raw,
  CodeExecutionPackage
> = objectSchema({
  version: stringSchema(),
  name: stringSchema(),
});

export declare namespace CodeExecutionPackageSerializer {
  interface Raw {
    version: string;
    name: string;
  }
}

export const CodeExecutionNodeDataSerializer: ObjectSchema<
  CodeExecutionNodeDataSerializer.Raw,
  CodeExecutionNodeData
> = objectSchema({
  label: stringSchema(),
  outputId: propertySchema("output_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  logOutputId: propertySchema("log_output_id", stringSchema().optional()),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  codeInputId: propertySchema("code_input_id", stringSchema()),
  runtimeInputId: propertySchema("runtime_input_id", stringSchema()),
  outputType: propertySchema("output_type", VellumVariableTypeSerializer),
  packages: propertySchema(
    "packages",
    listSchema(CodeExecutionPackageSerializer).optional()
  ),
});

export declare namespace CodeExecutionNodeDataSerializer {
  interface Raw {
    label: string;
    output_id: string;
    error_output_id?: string | null;
    log_output_id?: string | null;
    source_handle_id: string;
    target_handle_id: string;
    code_input_id: string;
    runtime_input_id: string;
    output_type: VellumVariableTypeSerializer.Raw;
    packages?: CodeExecutionPackageSerializer.Raw[] | null;
  }
}

export const CodeExecutionNodeSerializer: ObjectSchema<
  CodeExecutionNodeSerializer.Raw,
  CodeExecutionNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("CODE_EXECUTION"),
  data: CodeExecutionNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema("display_data", anySchema().optional()),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace CodeExecutionNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "CODE_EXECUTION";
    data: CodeExecutionNodeDataSerializer.Raw;
  }
}

export const SearchNodeDataSerializer: ObjectSchema<
  SearchNodeDataSerializer.Raw,
  SearchNodeData
> = objectSchema({
  label: stringSchema(),
  resultsOutputId: propertySchema("results_output_id", stringSchema()),
  textOutputId: propertySchema("text_output_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  queryNodeInputId: propertySchema("query_node_input_id", stringSchema()),
  documentIndexNodeInputId: propertySchema(
    "document_index_node_input_id",
    stringSchema()
  ),
  weightsNodeInputId: propertySchema("weights_node_input_id", stringSchema()),
  limitNodeInputId: propertySchema("limit_node_input_id", stringSchema()),
  separatorNodeInputId: propertySchema(
    "separator_node_input_id",
    stringSchema()
  ),
  resultMergingEnabledNodeInputId: propertySchema(
    "result_merging_enabled_node_input_id",
    stringSchema()
  ),
  externalIdFiltersNodeInputId: propertySchema(
    "external_id_filters_node_input_id",
    stringSchema()
  ),
  metadataFiltersNodeInputId: propertySchema(
    "metadata_filters_node_input_id",
    stringSchema()
  ),
});

export declare namespace SearchNodeDataSerializer {
  interface Raw {
    label: string;
    results_output_id: string;
    text_output_id: string;
    error_output_id?: string | null;
    source_handle_id: string;
    target_handle_id: string;
    query_node_input_id: string;
    document_index_node_input_id: string;
    weights_node_input_id: string;
    limit_node_input_id: string;
    separator_node_input_id: string;
    result_merging_enabled_node_input_id: string;
    external_id_filters_node_input_id: string;
    metadata_filters_node_input_id: string;
  }
}

export const SearchNodeSerializer: ObjectSchema<
  SearchNodeSerializer.Raw,
  SearchNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("SEARCH"),
  data: SearchNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace SearchNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "SEARCH";
    data: SearchNodeDataSerializer.Raw;
  }
}

export const ConditionalRuleDataSerializer: ObjectSchema<
  ConditionalRuleDataSerializer.Raw,
  ConditionalRuleData
> = objectSchema({
  id: stringSchema(),
  rules: listSchema(lazy(() => ConditionalRuleDataSerializer)).optional(),
  combinator: stringSchema().optional(),
  negated: booleanSchema().optional(),
  fieldNodeInputId: propertySchema(
    "field_node_input_id",
    stringSchema().optional()
  ),
  operator: stringSchema().optional(),
  valueNodeInputId: propertySchema(
    "value_node_input_id",
    stringSchema().optional()
  ),
});

export declare namespace ConditionalRuleDataSerializer {
  interface Raw {
    id: string;
    rules?: ConditionalRuleDataSerializer.Raw[] | null;
    combinator?: string | null;
    negated?: boolean | null;
    field_node_input_id?: string | null;
    operator?: string | null;
    value_node_input_id?: string | null;
  }
}

export const ConditionalNodeConditionDataSerializer: ObjectSchema<
  ConditionalNodeConditionDataSerializer.Raw,
  ConditionalNodeConditionData
> = objectSchema({
  id: stringSchema(),
  type: stringSchema(),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  data: ConditionalRuleDataSerializer.optional(),
});

export declare namespace ConditionalNodeConditionDataSerializer {
  interface Raw {
    id: string;
    type: string;
    source_handle_id: string;
    data?: ConditionalRuleDataSerializer.Raw | null;
  }
}

export const ConditionalNodeDataSerializer: ObjectSchema<
  ConditionalNodeDataSerializer.Raw,
  ConditionalNodeData
> = objectSchema({
  label: stringSchema(),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  conditions: listSchema(ConditionalNodeConditionDataSerializer),
  version: stringSchema(),
});

export declare namespace ConditionalNodeDataSerializer {
  interface Raw {
    label: string;
    target_handle_id: string;
    conditions: ConditionalNodeConditionDataSerializer.Raw[];
    version: string;
  }
}

export const ConditionalNodeSerializer: ObjectSchema<
  ConditionalNodeSerializer.Raw,
  ConditionalNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("CONDITIONAL"),
  data: ConditionalNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace ConditionalNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "CONDITIONAL";
    data: ConditionalNodeDataSerializer.Raw;
  }
}

export const TemplatingNodeSerializer: ObjectSchema<
  TemplatingNodeSerializer.Raw,
  TemplatingNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("TEMPLATING"),
  data: objectSchema({
    label: stringSchema(),
    outputId: propertySchema("output_id", stringSchema()),
    errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
    sourceHandleId: propertySchema("source_handle_id", stringSchema()),
    targetHandleId: propertySchema("target_handle_id", stringSchema()),
    templateNodeInputId: propertySchema(
      "template_node_input_id",
      stringSchema()
    ),
    outputType: propertySchema("output_type", VellumVariableTypeSerializer),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace TemplatingNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "TEMPLATING";
    data: {
      label: string;
      output_id: string;
      error_output_id?: string | null;
      source_handle_id: string;
      target_handle_id: string;
      template_node_input_id: string;
      output_type: VellumVariableTypeSerializer.Raw;
    };
  }
}

export const FinalOutputNodeSerializer: ObjectSchema<
  FinalOutputNodeSerializer.Raw,
  FinalOutputNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("TERMINAL"),
  data: objectSchema({
    label: stringSchema(),
    name: stringSchema(),
    targetHandleId: propertySchema("target_handle_id", stringSchema()),
    outputId: propertySchema("output_id", stringSchema()),
    outputType: propertySchema("output_type", VellumVariableTypeSerializer),
    nodeInputId: propertySchema("node_input_id", stringSchema()),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace FinalOutputNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "TERMINAL";
    data: {
      label: string;
      name: string;
      target_handle_id: string;
      output_id: string;
      output_type: VellumVariableTypeSerializer.Raw;
      node_input_id: string;
    };
  }
}

export const MergeNodeTargetHandleSerializer: ObjectSchema<
  MergeNodeTargetHandleSerializer.Raw,
  MergeNodeTargetHandle
> = objectSchema({
  id: stringSchema(),
});

export declare namespace MergeNodeTargetHandleSerializer {
  interface Raw {
    id: string;
  }
}

export const MergeNodeSerializer: ObjectSchema<
  MergeNodeSerializer.Raw,
  MergeNode
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("MERGE"),
  data: objectSchema({
    label: stringSchema(),
    mergeStrategy: propertySchema(
      "merge_strategy",
      undiscriminatedUnionSchema([
        stringLiteralSchema("AWAIT_ANY"),
        stringLiteralSchema("AWAIT_ALL"),
      ])
    ),
    targetHandles: propertySchema(
      "target_handles",
      listSchema(MergeNodeTargetHandleSerializer)
    ),
    sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace MergeNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "MERGE";
    data: {
      label: string;
      merge_strategy: "AWAIT_ALL" | "AWAIT_ANY";
      target_handles: MergeNodeTargetHandleSerializer.Raw[];
      source_handle_id: string;
    };
  }
}

export const ApiNodeAdditionalHeaderDataSerializer: ObjectSchema<
  ApiNodeAdditionalHeaderDataSerializer.Raw,
  ApiNodeAdditionalHeaderData
> = objectSchema({
  headerKeyInputId: propertySchema("header_key_input_id", stringSchema()),
  headerValueInputId: propertySchema("header_value_input_id", stringSchema()),
});

export declare namespace ApiNodeAdditionalHeaderDataSerializer {
  interface Raw {
    header_key_input_id: string;
    header_value_input_id: string;
  }
}

export const ApiNodeSerializer: ObjectSchema<ApiNodeSerializer.Raw, ApiNode> =
  objectSchema({
    id: stringSchema(),
    type: stringLiteralSchema("API"),
    data: objectSchema({
      label: stringSchema(),
      methodInputId: propertySchema("method_input_id", stringSchema()),
      urlInputId: propertySchema("url_input_id", stringSchema()),
      bodyInputId: propertySchema("body_input_id", stringSchema()),
      authorizationTypeInputId: propertySchema(
        "authorization_type_input_id",
        stringSchema().optional()
      ),
      bearerTokenValueInputId: propertySchema(
        "bearer_token_value_input_id",
        stringSchema().optional()
      ),
      apiKeyHeaderKeyInputId: propertySchema(
        "api_key_header_key_input_id",
        stringSchema().optional()
      ),
      apiKeyHeaderValueInputId: propertySchema(
        "api_key_header_value_input_id",
        stringSchema().optional()
      ),
      additionalHeaders: propertySchema(
        "additional_headers",
        listSchema(ApiNodeAdditionalHeaderDataSerializer).optional()
      ),
      textOutputId: propertySchema("text_output_id", stringSchema()),
      jsonOutputId: propertySchema("json_output_id", stringSchema()),
      statusCodeOutputId: propertySchema(
        "status_code_output_id",
        stringSchema()
      ),
      errorOutputId: propertySchema(
        "error_output_id",
        stringSchema().optional()
      ),
      targetHandleId: propertySchema("target_handle_id", stringSchema()),
      sourceHandleId: propertySchema("source_handle_id", stringSchema()),
    }),
    inputs: listSchema(NodeInputSerializer),
    displayData: propertySchema(
      "display_data",
      NodeDisplayDataSerializer.optional()
    ),
    definition: WorkflowNodeDefinitionSerializer.optional(),
  });

export declare namespace ApiNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "API";
    data: {
      label: string;
      method_input_id: string;
      url_input_id: string;
      body_input_id: string;
      authorization_type_input_id?: string | null;
      bearer_token_value_input_id?: string | null;
      api_key_header_key_input_id?: string | null;
      api_key_header_value_input_id?: string | null;
      additional_headers?: ApiNodeAdditionalHeaderDataSerializer.Raw[] | null;
      text_output_id: string;
      json_output_id: string;
      status_code_output_id: string;
      error_output_id?: string | null;
      target_handle_id: string;
      source_handle_id: string;
    };
  }
}

export const NoteNodeSerializer: ObjectSchema<
  NoteNodeSerializer.Raw,
  NoteNode
> = objectSchema({
  type: stringLiteralSchema("NOTE"),
  id: stringSchema(),
  data: objectSchema({
    label: stringSchema(),
    text: stringSchema().optional(),
    style: anySchema().optional(),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace NoteNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "NOTE";
    data: {
      label: string;
      text?: string | null | undefined;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      style?: Record<string, any> | null;
    };
  }
}

export const ErrorNodeSerializer: ObjectSchema<
  ErrorNodeSerializer.Raw,
  ErrorNode
> = objectSchema({
  type: stringLiteralSchema("ERROR"),
  id: stringSchema(),
  data: objectSchema({
    label: stringSchema(),
    name: stringSchema(),
    targetHandleId: propertySchema("target_handle_id", stringSchema()),
    errorSourceInputId: propertySchema("error_source_input_id", stringSchema()),
    errorOutputId: propertySchema("error_output_id", stringSchema()),
    sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace ErrorNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    type: "ERROR";
    data: {
      label: string;
      name: string;
      target_handle_id: string;
      error_source_input_id: string;
      error_output_id: string;
    };
  }
}

export const GenericNodeDisplayDataSerializer: ObjectSchema<
  GenericNodeDisplayDataSerializer.Raw,
  GenericNodeDisplayData
> = objectSchema({
  position: NodeDisplayPositionSerializer.optional(),
});

export declare namespace GenericNodeDisplayDataSerializer {
  interface Raw {
    position?: NodeDisplayPositionSerializer.Raw | null;
  }
}

export const GenericNodeSerializer: ObjectSchema<
  GenericNodeSerializer.Raw,
  GenericNode
> = objectSchema({
  type: stringLiteralSchema("GENERIC"),
  displayData: propertySchema(
    "display_data",
    GenericNodeDisplayDataSerializer.optional()
  ),
  definition: WorkflowNodeDefinitionSerializer.optional(),
});

export declare namespace GenericNodeSerializer {
  interface Raw extends BaseWorkflowNodeSerializer.Raw {
    type: "GENERIC";
    display_data?: {
      position?: {
        x: number;
        y: number;
      } | null;
    } | null;
  }
}

export const WorkflowNodeSerializer: Schema<
  WorkflowNodeSerializer.Raw,
  WorkflowNode
> = undiscriminatedUnionSchema([
  EntrypointNodeSerializer,
  PromptNodeSerializer,
  SearchNodeSerializer,
  SubworkflowNodeSerializer,
  MapNodeSerializer,
  GuardrailNodeSerializer,
  CodeExecutionNodeSerializer,
  FinalOutputNodeSerializer,
  MergeNodeSerializer,
  TemplatingNodeSerializer,
  ConditionalNodeSerializer,
  ApiNodeSerializer,
  NoteNodeSerializer,
  ErrorNodeSerializer,
  GenericNodeSerializer,
]);

export declare namespace WorkflowNodeSerializer {
  type Raw =
    | EntrypointNodeSerializer.Raw
    | PromptNodeSerializer.Raw
    | SearchNodeSerializer.Raw
    | SubworkflowNodeSerializer.Raw
    | MapNodeSerializer.Raw
    | GuardrailNodeSerializer.Raw
    | FinalOutputNodeSerializer.Raw
    | MergeNodeSerializer.Raw
    | CodeExecutionNodeSerializer.Raw
    | TemplatingNodeSerializer.Raw
    | ConditionalNodeSerializer.Raw
    | ApiNodeSerializer.Raw
    | NoteNodeSerializer.Raw
    | ErrorNodeSerializer.Raw
    | GenericNodeSerializer.Raw;
}

const workflowEdgeSerializer: ObjectSchema<
  WorkflowEdgeSerializer.Raw,
  WorkflowEdge
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("DEFAULT"),
  sourceNodeId: propertySchema("source_node_id", stringSchema()),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetNodeId: propertySchema("target_node_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
});

export declare namespace WorkflowEdgeSerializer {
  interface Raw {
    id: string;
    type: "DEFAULT";
    source_node_id: string;
    source_handle_id: string;
    target_node_id: string;
    target_handle_id: string;
  }
}

export const WorkflowRawDataSerializer: ObjectSchema<
  WorkflowRawDataSerializer.Raw,
  WorkflowRawData
> = objectSchema({
  nodes: listSchema(WorkflowNodeSerializer),
  edges: listSchema(workflowEdgeSerializer),
  displayData: propertySchema("display_data", anySchema()),
  definition: CodeResourceDefinitionSerializer.optional(),
});

export declare namespace WorkflowRawDataSerializer {
  interface Raw {
    nodes: WorkflowNodeSerializer.Raw[];
    edges: WorkflowEdgeSerializer.Raw[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    display_data?: any;
    definition?: CodeResourceDefinitionSerializer.Raw | null;
  }
}

export const WorkflowVersionExecConfigSerializer: ObjectSchema<
  WorkflowVersionExecConfigSerializer.Raw,
  WorkflowVersionExecConfig
> = objectSchema({
  workflowRawData: propertySchema(
    "workflow_raw_data",
    WorkflowRawDataSerializer
  ),
  inputVariables: propertySchema(
    "input_variables",
    listSchema(VellumVariableSerializer)
  ),
  outputVariables: propertySchema(
    "output_variables",
    listSchema(VellumVariableSerializer)
  ),
  runnerConfig: propertySchema(
    "runner_config",
    objectSchema({
      containerImageName: propertySchema(
        "container_image_name",
        stringSchema()
      ),
      containerImageTag: propertySchema("container_image_tag", stringSchema()),
    }).optional()
  ),
});

export declare namespace WorkflowVersionExecConfigSerializer {
  interface Raw {
    workflow_raw_data: WorkflowRawDataSerializer.Raw;
    input_variables: VellumVariableSerializer.Raw[];
    output_variables: VellumVariableSerializer.Raw[];
    runner_config?: {
      container_image_name: string;
      container_image_tag: string;
    } | null;
  }
}

export const WorkflowEdgeSerializer: ObjectSchema<
  WorkflowEdgeSerializer.Raw,
  WorkflowEdge
> = objectSchema({
  id: stringSchema(),
  type: stringLiteralSchema("DEFAULT"),
  sourceNodeId: propertySchema("source_node_id", stringSchema()),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetNodeId: propertySchema("target_node_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
});

export declare namespace WorkflowEdgeSerializer {
  interface Raw {
    id: string;
    source_node_id: string;
    source_handle_id: string;
    target_node_id: string;
    target_handle_id: string;
  }
}

export const WorkflowDisplayDataViewportSerializer: ObjectSchema<
  WorkflowDisplayDataViewportSerializer.Raw,
  WorkflowDisplayDataViewport
> = objectSchema({
  x: numberSchema(),
  y: numberSchema(),
  zoom: numberSchema(),
});

export declare namespace WorkflowDisplayDataViewportSerializer {
  interface Raw {
    x: number;
    y: number;
    zoom: number;
  }
}

export const WorkflowDisplayDataSerializer: ObjectSchema<
  WorkflowDisplayDataSerializer.Raw,
  WorkflowDisplayData
> = objectSchema({
  viewport: WorkflowDisplayDataViewportSerializer,
});

export declare namespace WorkflowDisplayDataSerializer {
  interface Raw {
    viewport: WorkflowDisplayDataViewportSerializer.Raw;
  }
}
