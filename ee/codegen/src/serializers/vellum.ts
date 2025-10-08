import { ChatMessageRole, PromptBlockState } from "vellum-ai/api";
import {
  any as anySchema,
  boolean,
  boolean as booleanSchema,
  lazy as lazySchema,
  list as listSchema,
  number as numberSchema,
  object as objectSchema,
  ObjectSchema,
  property as propertySchema,
  record as recordSchema,
  Schema,
  stringLiteral as stringLiteralSchema,
  string as stringSchema,
  undiscriminatedUnion as undiscriminatedUnionSchema,
  union as unionSchema,
  unknown as unknownSchema,
} from "vellum-ai/core/schemas";
import {
  ChatMessageRole as ChatMessageRoleSerializer,
  LogicalOperator as LogicalOperatorSerializer,
  PromptBlockState as PromptBlockStateSerializer,
  PromptParameters as PromptParametersSerializer,
  VellumValue as VellumValueSerializer,
  VellumVariable as VellumVariableSerializer,
  VellumVariableType as VellumVariableTypeSerializer,
} from "vellum-ai/serialization";
import { ConditionCombinator as ConditionCombinatorSerializer } from "vellum-ai/serialization/types/ConditionCombinator";

import {
  AdornmentNode,
  ApiNode,
  ApiNodeAdditionalHeaderData,
  ArrayWorkflowReference,
  BinaryWorkflowExpression,
  ChatMessagePromptTemplateBlock,
  CodeExecutionNode,
  CodeExecutionNodeData,
  CodeExecutionPackage,
  CodeResourceDefinition,
  ConditionalNode,
  ConditionalNodeConditionData,
  ConditionalNodeData,
  ConditionalRuleData,
  ConstantValuePointer,
  ConstantValueWorkflowReference,
  DefaultNodePort,
  DeploymentMapNodeData,
  DeploymentPromptNodeData,
  DeploymentSubworkflowNodeData,
  DictionaryWorkflowReference,
  DictionaryWorkflowReferenceEntry,
  ElifConditionNodePort,
  ElseConditionNodePort,
  EntrypointNode,
  EnvironmentVariablePointer,
  EnvironmentVariableWorkflowReference,
  ErrorNode,
  ExecutionCounterPointer,
  ExecutionCounterWorkflowReference,
  FinalOutputNode,
  FunctionDefinitionPromptTemplateBlock,
  GenericNode,
  GenericNodeDisplayData,
  GuardrailNode,
  IfConditionNodePort,
  InlineMapNodeData,
  InlinePromptNodeData,
  InlineSubworkflowNodeData,
  InputVariablePointer,
  JinjaPromptTemplateBlock,
  LegacyPromptNodeData,
  MapNode,
  MapNodeData,
  MergeNode,
  MergeNodeTargetHandle,
  NodeAttribute,
  NodeDisplayComment,
  NodeDisplayData,
  NodeDisplayPosition,
  NodeInput,
  NodeInputValuePointerRule,
  NodeOutput,
  NodeOutputPointer,
  NodeOutputWorkflowReference,
  NodeTrigger,
  NoteNode,
  PlainTextPromptTemplateBlock,
  PromptNode,
  PromptNodeData,
  PromptNodeDeployment,
  PromptNodeSourceSandbox,
  PromptSettings,
  PromptTemplateBlock,
  PromptTemplateBlockData,
  PromptVersionData,
  PromptVersionExecConfig,
  RichTextChildPromptTemplateBlock,
  RichTextPromptTemplateBlock,
  SearchNode,
  SearchNodeData,
  SubworkflowNode,
  TemplatingNode,
  TernaryWorkflowExpression,
  UnaryWorkflowExpression,
  VariablePromptTemplateBlock,
  VellumLogicalCondition,
  VellumLogicalConditionGroup,
  VellumLogicalExpression,
  VellumSecretWorkflowReference,
  WorkflowDisplayData,
  WorkflowDisplayDataViewport,
  WorkflowEdge,
  WorkflowEdgeDisplayData,
  WorkflowInputWorkflowReference,
  WorkflowNode,
  WorkflowOutputValue,
  WorkflowRawData,
  WorkflowSandboxRoutingConfig,
  WorkflowStateVariableWorkflowReference,
  WorkflowTrigger,
  WorkflowValueDescriptor,
  WorkspaceSecretPointer,
} from "src/types/vellum";

const CacheConfigSerializer = objectSchema({
  type: stringLiteralSchema("EPHEMERAL").optional(),
});

export const JinjaPromptTemplateBlockSerializer: ObjectSchema<
  JinjaPromptTemplateBlockSerializer.Raw,
  Omit<JinjaPromptTemplateBlock, "blockType">
> = objectSchema({
  id: stringSchema(),
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
    state: PromptBlockState;
    cache_config?: { type?: "EPHEMERAL" | null } | null;
    properties: {
      template?: string | null;
      template_type?: string | null;
    };
  }
}

export const ChatMessagePromptTemplateBlockSerializer: ObjectSchema<
  ChatMessagePromptTemplateBlockSerializer.Raw,
  Omit<ChatMessagePromptTemplateBlock, "blockType">
> = objectSchema({
  id: stringSchema(),
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
      listSchema(
        lazySchema(() => {
          return PromptTemplateBlockSerializer as unknown as Schema<
            PromptTemplateBlockSerializer.Raw,
            PromptTemplateBlock
          >;
        })
      )
    ),
  }),
});

export declare namespace ChatMessagePromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    state: PromptBlockState;
    cache_config?: { type?: "EPHEMERAL" | null } | null;
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
  Omit<VariablePromptTemplateBlock, "blockType">
> = objectSchema({
  id: stringSchema(),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  inputVariableId: propertySchema("input_variable_id", stringSchema()),
});

export declare namespace VariablePromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    state: PromptBlockState;
    cache_config?: { type?: "EPHEMERAL" | null } | null;
    input_variable_id: string;
  }
}

export const PlainTextPromptTemplateBlockSerializer: ObjectSchema<
  PlainTextPromptTemplateBlockSerializer.Raw,
  Omit<PlainTextPromptTemplateBlock, "blockType">
> = objectSchema({
  id: stringSchema(),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  text: stringSchema(),
});

export declare namespace PlainTextPromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    state: PromptBlockState;
    cache_config?: { type?: "EPHEMERAL" | null } | null;
    text: string;
  }
}

export const RichTextPromptTemplateBlockSerializer: ObjectSchema<
  RichTextPromptTemplateBlockSerializer.Raw,
  Omit<RichTextPromptTemplateBlock, "blockType">
> = objectSchema({
  id: stringSchema(),
  state: propertySchema("state", PromptBlockStateSerializer),
  cacheConfig: propertySchema("cache_config", CacheConfigSerializer.optional()),
  blocks: listSchema(
    unionSchema(
      {
        parsedDiscriminant: "blockType",
        rawDiscriminant: "block_type",
      },
      {
        PLAIN_TEXT: PlainTextPromptTemplateBlockSerializer,
        VARIABLE: VariablePromptTemplateBlockSerializer,
      }
    ) as unknown as Schema<
      | PlainTextPromptTemplateBlockSerializer.Raw
      | VariablePromptTemplateBlockSerializer.Raw,
      RichTextChildPromptTemplateBlock
    >
  ),
});

export declare namespace RichTextPromptTemplateBlockSerializer {
  interface Raw {
    id: string;
    state: PromptBlockState;
    cache_config?: { type?: "EPHEMERAL" | null } | null;
    blocks: Array<
      | PlainTextPromptTemplateBlockSerializer.Raw
      | VariablePromptTemplateBlockSerializer.Raw
    >;
  }
}

export const FunctionDefinitionPromptTemplateBlockSerializer: ObjectSchema<
  FunctionDefinitionPromptTemplateBlockSerializer.Raw,
  Omit<FunctionDefinitionPromptTemplateBlock, "blockType">
> = objectSchema({
  id: stringSchema(),
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
    state: PromptBlockState;
    cache_config?: { type?: "EPHEMERAL" | null } | null;
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

const PromptTemplateBlockSerializer = unionSchema(
  { parsedDiscriminant: "blockType", rawDiscriminant: "block_type" },
  {
    JINJA: JinjaPromptTemplateBlockSerializer,
    CHAT_MESSAGE: ChatMessagePromptTemplateBlockSerializer,
    VARIABLE: VariablePromptTemplateBlockSerializer,
    RICH_TEXT: RichTextPromptTemplateBlockSerializer,
    FUNCTION_DEFINITION: FunctionDefinitionPromptTemplateBlockSerializer,
  }
);

export const NodeOutputPointerSerializer: ObjectSchema<
  NodeOutputPointerSerializer.Raw,
  Omit<NodeOutputPointer, "type">
> = objectSchema({
  data: objectSchema({
    nodeId: propertySchema("node_id", stringSchema()),
    outputId: propertySchema("output_id", stringSchema()),
  }),
});

export declare namespace NodeOutputPointerSerializer {
  interface Raw {
    data: {
      node_id: string;
    };
  }
}

export const InputVariablePointerSerializer: ObjectSchema<
  InputVariablePointerSerializer.Raw,
  Omit<InputVariablePointer, "type">
> = objectSchema({
  data: objectSchema({
    inputVariableId: propertySchema("input_variable_id", stringSchema()),
  }),
});

export declare namespace InputVariablePointerSerializer {
  interface Raw {
    data: {
      input_variable_id: string;
    };
  }
}

export const ConstantValuePointerSerializer: ObjectSchema<
  ConstantValuePointerSerializer.Raw,
  Omit<ConstantValuePointer, "type">
> = objectSchema({
  data: VellumValueSerializer,
});

export declare namespace ConstantValuePointerSerializer {
  interface Raw {
    data: VellumValueSerializer.Raw;
  }
}

export declare namespace VellumValueLogicalConditionSerializer {
  interface Raw {
    lhs_variable_id: string;
    operator: LogicalOperatorSerializer.Raw;
    rhs_variable_id: string;
  }
}

export const VellumValueLogicalConditionSerializer: ObjectSchema<
  VellumValueLogicalConditionSerializer.Raw,
  Omit<VellumLogicalCondition, "type">
> = objectSchema({
  lhsVariableId: propertySchema("lhs_variable_id", stringSchema()),
  operator: LogicalOperatorSerializer,
  rhsVariableId: propertySchema("rhs_variable_id", stringSchema()),
});

export declare namespace VellumValueLogicalConditionGroupSerializer {
  interface Raw {
    conditions: VellumValueLogicalExpressionSerializer.Raw[];
    combinator: ConditionCombinatorSerializer.Raw;
    negated: boolean;
  }
}

export const VellumValueLogicalConditionGroupSerializer: ObjectSchema<
  VellumValueLogicalConditionGroupSerializer.Raw,
  Omit<VellumLogicalConditionGroup, "type">
> = objectSchema({
  conditions: listSchema(
    lazySchema(() => VellumValueLogicalExpressionSerializer)
  ),
  combinator: ConditionCombinatorSerializer,
  negated: boolean(),
});

export declare namespace VellumValueLogicalExpressionSerializer {
  type Raw =
    | VellumValueLogicalConditionSerializer.Raw
    | VellumValueLogicalConditionGroupSerializer.Raw;
}

export const VellumValueLogicalExpressionSerializer: Schema<
  VellumValueLogicalExpressionSerializer.Raw,
  VellumLogicalExpression
> = unionSchema("type", {
  LOGICAL_CONDITION_GROUP: VellumValueLogicalConditionGroupSerializer,
  LOGICAL_CONDITION: VellumValueLogicalConditionSerializer,
});

export const WorkspaceSecretPointerSerializer: ObjectSchema<
  WorkspaceSecretPointerSerializer.Raw,
  Omit<WorkspaceSecretPointer, "type">
> = objectSchema({
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
    data: {
      type: "STRING";
      workspace_secret_id?: string | null | undefined;
    };
  }
}

export const ExecutionCounterPointerSerializer: ObjectSchema<
  ExecutionCounterPointerSerializer.Raw,
  Omit<ExecutionCounterPointer, "type">
> = objectSchema({
  data: objectSchema({
    nodeId: propertySchema("node_id", stringSchema()),
  }),
});

export declare namespace ExecutionCounterPointerSerializer {
  interface Raw {
    data: {
      node_id: string;
    };
  }
}

export const EnvironmentVariablePointerSerializer: ObjectSchema<
  EnvironmentVariablePointerSerializer.Raw,
  Omit<EnvironmentVariablePointer, "type">
> = objectSchema({
  data: objectSchema({
    environmentVariable: propertySchema("environment_variable", stringSchema()),
  }),
});

export declare namespace EnvironmentVariablePointerSerializer {
  interface Raw {
    data: {
      environment_variable: string;
    };
  }
}

export const NodeInputValuePointerRuleSerializer: Schema<
  NodeInputValuePointerRuleSerializer.Raw,
  NodeInputValuePointerRule
> = unionSchema("type", {
  NODE_OUTPUT: NodeOutputPointerSerializer,
  INPUT_VARIABLE: InputVariablePointerSerializer,
  CONSTANT_VALUE: ConstantValuePointerSerializer,
  WORKSPACE_SECRET: WorkspaceSecretPointerSerializer,
  EXECUTION_COUNTER: ExecutionCounterPointerSerializer,
  ENVIRONMENT_VARIABLE: EnvironmentVariablePointerSerializer,
});

export declare namespace NodeInputValuePointerRuleSerializer {
  type Raw =
    | NodeOutputPointerSerializer.Raw
    | InputVariablePointerSerializer.Raw
    | ConstantValuePointerSerializer.Raw
    | WorkspaceSecretPointerSerializer.Raw
    | ExecutionCounterPointerSerializer.Raw
    | EnvironmentVariablePointerSerializer.Raw;
}

export const NodeInputSerializer: ObjectSchema<
  NodeInputSerializer.Raw,
  NodeInput
> = objectSchema({
  id: stringSchema(),
  key: stringSchema(),
  value: objectSchema({
    rules: listSchema(NodeInputValuePointerRuleSerializer),
    combinator: undiscriminatedUnionSchema([
      stringLiteralSchema("OR"),
      stringLiteralSchema("AND"),
    ]).transform({
      transform: () => "OR" as const,
      untransform: () => "OR" as const,
    }),
  }),
});

export declare namespace NodeInputSerializer {
  interface Raw {
    id: string;
    key: string;
    value: {
      rules: NodeInputValuePointerRuleSerializer.Raw[];
      combinator: "OR" | "AND";
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

export const PromptTemplateBlockDataSerializer: ObjectSchema<
  PromptTemplateBlockDataSerializer.Raw,
  PromptTemplateBlockData
> = objectSchema({
  version: numberSchema(),
  blocks: listSchema(
    PromptTemplateBlockSerializer as unknown as Schema<
      PromptTemplateBlockSerializer.Raw,
      PromptTemplateBlock
    >
  ),
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
  timeout: numberSchema().nullable().optional(),
  streamEnabled: propertySchema(
    "stream_enabled",
    booleanSchema().nullable().optional()
  ),
});

export declare namespace PromptSettingsSerializer {
  interface Raw {
    timeout?: number | null;
    stream_enabled?: boolean | null;
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
  z_index: numberSchema().optional(),
  width: numberSchema().optional(),
  height: numberSchema().optional(),
  comment: NodeDisplayCommentSerializer.optional(),
  color: stringSchema().nullable().optional(),
  icon: stringSchema().nullable().optional(),
});

export declare namespace NodeDisplayDataSerializer {
  interface Raw {
    position?: NodeDisplayPositionSerializer.Raw | null;
    z_index?: number | null;
    width?: number | null;
    height?: number | null;
    comment?: NodeDisplayCommentSerializer.Raw | null;
    color?: string | null;
    icon?: string | null;
  }
}

export const WorkflowEdgeDisplayDataSerializer: ObjectSchema<
  WorkflowEdgeDisplayDataSerializer.Raw,
  WorkflowEdgeDisplayData
> = objectSchema({
  z_index: numberSchema().optional(),
});

export declare namespace WorkflowEdgeDisplayDataSerializer {
  interface Raw {
    z_index?: number | null;
  }
}

export const UnaryWorkflowExpressionSerializer: ObjectSchema<
  UnaryWorkflowExpressionSerializer.Raw,
  Omit<UnaryWorkflowExpression, "type">
> = objectSchema({
  lhs: lazySchema(() => WorkflowValueDescriptorSerializer).optional(),
  operator: LogicalOperatorSerializer,
});

export declare namespace UnaryWorkflowExpressionSerializer {
  interface Raw {
    lhs?: WorkflowValueDescriptorSerializer.Raw | null;
    operator: LogicalOperatorSerializer.Raw;
  }
}

export const BinaryWorkflowExpressionSerializer: ObjectSchema<
  BinaryWorkflowExpressionSerializer.Raw,
  Omit<BinaryWorkflowExpression, "type">
> = objectSchema({
  lhs: lazySchema(() => WorkflowValueDescriptorSerializer).optional(),
  operator: LogicalOperatorSerializer,
  rhs: lazySchema(() => WorkflowValueDescriptorSerializer).optional(),
});

export declare namespace BinaryWorkflowExpressionSerializer {
  interface Raw {
    lhs?: WorkflowValueDescriptorSerializer.Raw | null;
    operator: LogicalOperatorSerializer.Raw;
    rhs?: WorkflowValueDescriptorSerializer.Raw | null;
  }
}

export const TernaryWorkflowExpressionSerializer: ObjectSchema<
  TernaryWorkflowExpressionSerializer.Raw,
  Omit<TernaryWorkflowExpression, "type">
> = objectSchema({
  base: lazySchema(() => WorkflowValueDescriptorSerializer).optional(),
  operator: LogicalOperatorSerializer,
  lhs: lazySchema(() => WorkflowValueDescriptorSerializer).optional(),
  rhs: lazySchema(() => WorkflowValueDescriptorSerializer).optional(),
});

export declare namespace TernaryWorkflowExpressionSerializer {
  interface Raw {
    base?: WorkflowValueDescriptorSerializer.Raw | null;
    operator: LogicalOperatorSerializer.Raw;
    lhs?: WorkflowValueDescriptorSerializer.Raw | null;
    rhs?: WorkflowValueDescriptorSerializer.Raw | null;
  }
}

export const NodeOutputWorkflowReferenceSerializer: ObjectSchema<
  NodeOutputWorkflowReferenceSerializer.Raw,
  Omit<NodeOutputWorkflowReference, "type">
> = objectSchema({
  nodeId: propertySchema("node_id", stringSchema()),
  nodeOutputId: propertySchema("node_output_id", stringSchema()),
});

export declare namespace NodeOutputWorkflowReferenceSerializer {
  interface Raw {
    node_id: string;
    node_output_id: string;
  }
}

export const WorkflowInputWorkflowReferenceSerializer: ObjectSchema<
  WorkflowInputWorkflowReferenceSerializer.Raw,
  Omit<WorkflowInputWorkflowReference, "type">
> = objectSchema({
  inputVariableId: propertySchema("input_variable_id", stringSchema()),
});

export declare namespace WorkflowInputWorkflowReferenceSerializer {
  interface Raw {
    input_variable_id: string;
  }
}

export const WorkflowStateVariableWorkflowReferenceSerializer: ObjectSchema<
  WorkflowStateVariableWorkflowReferenceSerializer.Raw,
  Omit<WorkflowStateVariableWorkflowReference, "type">
> = objectSchema({
  stateVariableId: propertySchema("state_variable_id", stringSchema()),
});

export declare namespace WorkflowStateVariableWorkflowReferenceSerializer {
  interface Raw {
    state_variable_id: string;
  }
}

export const ConstantValueWorkflowReferenceSerializer: ObjectSchema<
  ConstantValueWorkflowReferenceSerializer.Raw,
  Omit<ConstantValueWorkflowReference, "type">
> = objectSchema({
  value: VellumValueSerializer,
});

export declare namespace ConstantValueWorkflowReferenceSerializer {
  interface Raw {
    value: VellumValueSerializer.Raw;
  }
}

export const VellumSecretWorkflowReferenceSerializer: ObjectSchema<
  VellumSecretWorkflowReferenceSerializer.Raw,
  Omit<VellumSecretWorkflowReference, "type">
> = objectSchema({
  vellumSecretName: propertySchema("vellum_secret_name", stringSchema()),
});

export declare namespace VellumSecretWorkflowReferenceSerializer {
  interface Raw {
    vellum_secret_name: string;
  }
}

export const EnvironmentVariableWorkflowReferenceSerializer: ObjectSchema<
  EnvironmentVariableWorkflowReferenceSerializer.Raw,
  Omit<EnvironmentVariableWorkflowReference, "type">
> = objectSchema({
  environmentVariable: propertySchema("environment_variable", stringSchema()),
});

export declare namespace EnvironmentVariableWorkflowReferenceSerializer {
  interface Raw {
    environment_variable: string;
  }
}

export const ExecutionCounterWorkflowReferenceSerializer: ObjectSchema<
  ExecutionCounterWorkflowReferenceSerializer.Raw,
  Omit<ExecutionCounterWorkflowReference, "type">
> = objectSchema({
  nodeId: propertySchema("node_id", stringSchema()),
});

export declare namespace ExecutionCounterWorkflowReferenceSerializer {
  interface Raw {
    node_id: string;
  }
}

export const DictionaryWorkflowReferenceEntrySerializer: ObjectSchema<
  DictionaryWorkflowReferenceEntrySerializer.Raw,
  Omit<DictionaryWorkflowReferenceEntry, "type">
> = objectSchema({
  id: stringSchema().optional(),
  key: stringSchema(),
  value: lazySchema(() => WorkflowValueDescriptorSerializer).nullable(),
});

export declare namespace DictionaryWorkflowReferenceEntrySerializer {
  interface Raw {
    id?: string | null;
    key: string;
    value: WorkflowValueDescriptorSerializer.Raw | null;
  }
}

export const DictionaryWorkflowReferenceSerializer: ObjectSchema<
  DictionaryWorkflowReferenceSerializer.Raw,
  Omit<DictionaryWorkflowReference, "type">
> = objectSchema({
  entries: listSchema(DictionaryWorkflowReferenceEntrySerializer),
});

export declare namespace DictionaryWorkflowReferenceSerializer {
  interface Raw {
    entries: DictionaryWorkflowReferenceEntrySerializer.Raw[];
  }
}

export const ArrayWorkflowReferenceSerializer: ObjectSchema<
  ArrayWorkflowReferenceSerializer.Raw,
  Omit<ArrayWorkflowReference, "type">
> = objectSchema({
  items: listSchema(lazySchema(() => WorkflowValueDescriptorSerializer)),
});

export declare namespace ArrayWorkflowReferenceSerializer {
  interface Raw {
    items: WorkflowValueDescriptorSerializer.Raw[];
  }
}

export const WorkflowValueDescriptorSerializer: Schema<
  WorkflowValueDescriptorSerializer.Raw,
  WorkflowValueDescriptor
> = unionSchema("type", {
  UNARY_EXPRESSION: UnaryWorkflowExpressionSerializer,
  BINARY_EXPRESSION: BinaryWorkflowExpressionSerializer,
  TERNARY_EXPRESSION: TernaryWorkflowExpressionSerializer,
  NODE_OUTPUT: NodeOutputWorkflowReferenceSerializer,
  WORKFLOW_INPUT: WorkflowInputWorkflowReferenceSerializer,
  WORKFLOW_STATE: WorkflowStateVariableWorkflowReferenceSerializer,
  CONSTANT_VALUE: ConstantValueWorkflowReferenceSerializer,
  VELLUM_SECRET: VellumSecretWorkflowReferenceSerializer,
  ENVIRONMENT_VARIABLE: EnvironmentVariableWorkflowReferenceSerializer,
  EXECUTION_COUNTER: ExecutionCounterWorkflowReferenceSerializer,
  DICTIONARY_REFERENCE: DictionaryWorkflowReferenceSerializer,
  ARRAY_REFERENCE: ArrayWorkflowReferenceSerializer,
});

export declare namespace WorkflowValueDescriptorSerializer {
  type Raw =
    | UnaryWorkflowExpressionSerializer.Raw
    | BinaryWorkflowExpressionSerializer.Raw
    | TernaryWorkflowExpressionSerializer.Raw
    | NodeOutputWorkflowReferenceSerializer.Raw
    | WorkflowInputWorkflowReferenceSerializer.Raw
    | WorkflowStateVariableWorkflowReferenceSerializer.Raw
    | ConstantValueWorkflowReferenceSerializer.Raw
    | VellumSecretWorkflowReferenceSerializer.Raw
    | EnvironmentVariableWorkflowReferenceSerializer.Raw
    | ExecutionCounterWorkflowReferenceSerializer.Raw
    | DictionaryWorkflowReferenceSerializer.Raw
    | ArrayWorkflowReferenceSerializer.Raw;
}

export const NodeOutputSerializer: ObjectSchema<
  NodeOutputSerializer.Raw,
  NodeOutput
> = objectSchema({
  id: stringSchema(),
  name: stringSchema(),
  type: VellumVariableTypeSerializer,
  value: WorkflowValueDescriptorSerializer.optional(),
});

export declare namespace NodeOutputSerializer {
  interface Raw {
    id: string;
    name: string;
    type: VellumVariableTypeSerializer.Raw;
    value?: WorkflowValueDescriptorSerializer.Raw | null;
  }
}

export const NodeAttributeSerializer: ObjectSchema<
  NodeAttributeSerializer.Raw,
  NodeAttribute
> = objectSchema({
  id: stringSchema(),
  name: stringSchema(),
  value: WorkflowValueDescriptorSerializer.optional().nullable(),
});

export declare namespace NodeAttributeSerializer {
  interface Raw {
    id: string;
    name: string;
    value?: WorkflowValueDescriptorSerializer.Raw | null;
  }
}

export const AdornmentNodeSerializer: ObjectSchema<
  AdornmentNodeSerializer.Raw,
  AdornmentNode
> = objectSchema({
  id: stringSchema(),
  label: stringSchema(),
  base: CodeResourceDefinitionSerializer,
  attributes: listSchema(NodeAttributeSerializer),
});

export declare namespace AdornmentNodeSerializer {
  interface Raw {
    id: string;
    label: string;
    base: CodeResourceDefinitionSerializer.Raw;
    attributes: NodeAttributeSerializer.Raw[];
  }
}

export const DefaultConditionNodePortSerializer: ObjectSchema<
  DefaultConditionNodePortSerializer.Raw,
  Omit<DefaultNodePort, "type">
> = objectSchema({
  id: stringSchema(),
  name: stringSchema(),
});

export declare namespace DefaultConditionNodePortSerializer {
  interface Raw {
    id: string;
    name: string;
  }
}

export const IfConditionNodePortSerializer: ObjectSchema<
  IfConditionNodePortSerializer.Raw,
  Omit<IfConditionNodePort, "type">
> = objectSchema({
  id: stringSchema(),
  name: stringSchema(),
  expression: WorkflowValueDescriptorSerializer.optional(),
});

export declare namespace IfConditionNodePortSerializer {
  interface Raw {
    id: string;
    name: string;
    expression?: WorkflowValueDescriptorSerializer.Raw | null;
  }
}

export const ElifConditionNodePortSerializer: ObjectSchema<
  ElifConditionNodePortSerializer.Raw,
  Omit<ElifConditionNodePort, "type">
> = objectSchema({
  id: stringSchema(),
  name: stringSchema(),
  expression: WorkflowValueDescriptorSerializer.optional(),
});

export declare namespace ElifConditionNodePortSerializer {
  interface Raw {
    id: string;
    name: string;
    expression?: WorkflowValueDescriptorSerializer.Raw | null;
  }
}

export const ElseConditionNodePortSerializer: ObjectSchema<
  ElseConditionNodePortSerializer.Raw,
  Omit<ElseConditionNodePort, "type">
> = objectSchema({
  id: stringSchema(),
  name: stringSchema(),
});

export declare namespace ElseConditionNodePortSerializer {
  interface Raw {
    id: string;
    name: string;
  }
}

const NodePortSerializer = unionSchema("type", {
  DEFAULT: DefaultConditionNodePortSerializer,
  IF: IfConditionNodePortSerializer,
  ELIF: ElifConditionNodePortSerializer,
  ELSE: ElseConditionNodePortSerializer,
});

export declare namespace NodePortSerializer {
  type Raw =
    | DefaultConditionNodePortSerializer.Raw
    | IfConditionNodePortSerializer.Raw
    | ElifConditionNodePortSerializer.Raw
    | ElseConditionNodePortSerializer.Raw;
}

export declare namespace NodeTriggerSerializer {
  interface Raw {
    id: string;
    merge_behavior: "AWAIT_ATTRIBUTES" | "AWAIT_ALL" | "AWAIT_ANY" | "CUSTOM";
  }
}

export const NodeTriggerSerializer: ObjectSchema<
  NodeTriggerSerializer.Raw,
  NodeTrigger
> = objectSchema({
  id: stringSchema(),
  mergeBehavior: propertySchema(
    "merge_behavior",
    undiscriminatedUnionSchema([
      stringLiteralSchema("AWAIT_ATTRIBUTES"),
      stringLiteralSchema("AWAIT_ALL"),
      stringLiteralSchema("AWAIT_ANY"),
      stringLiteralSchema("CUSTOM"),
    ])
  ),
});

export declare namespace BaseWorkflowNodeSerializer {
  interface Raw {
    base?: CodeResourceDefinitionSerializer.Raw | null;
    definition?: CodeResourceDefinitionSerializer.Raw | null;
    should_file_merge?: boolean | null;
  }
}

export declare namespace BaseDisplayableWorkflowNodeSerializer {
  interface Raw extends BaseWorkflowNodeSerializer.Raw {
    id: string;
    display_data?: NodeDisplayDataSerializer.Raw | null;
    inputs: NodeInputSerializer.Raw[];
    adornments?: AdornmentNodeSerializer.Raw[] | null;
    outputs?: NodeOutputSerializer.Raw[] | null;
    attributes?: NodeAttributeSerializer.Raw[] | null;
    ports?: NodePortSerializer.Raw[] | null;
    trigger?: NodeTriggerSerializer.Raw | null;
  }
}

export const EntrypointNodeSerializer: ObjectSchema<
  EntrypointNodeSerializer.Raw,
  Omit<EntrypointNode, "type">
> = objectSchema({
  id: stringSchema(),
  data: objectSchema({
    label: stringSchema(),
    sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
});

export declare namespace EntrypointNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    data: {
      label: string;
      source_handle_id: string;
    };
  }
}

export const InlineSubworkflowNodeDataSerializer: ObjectSchema<
  InlineSubworkflowNodeDataSerializer.Raw,
  Omit<InlineSubworkflowNodeData, "variant">
> = objectSchema({
  workflowRawData: propertySchema(
    "workflow_raw_data",
    lazySchema(() => WorkflowRawDataSerializer)
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
  }
}

export const DeploymentSubworkflowNodeDataSerializer: ObjectSchema<
  DeploymentSubworkflowNodeDataSerializer.Raw,
  Omit<DeploymentSubworkflowNodeData, "variant">
> = objectSchema({
  label: stringSchema(),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
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
    workflow_deployment_id: string;
    release_tag: string;
  }
}

export const SubworkflowNodeDataSerializer = unionSchema("variant", {
  INLINE: InlineSubworkflowNodeDataSerializer,
  DEPLOYMENT: DeploymentSubworkflowNodeDataSerializer,
});

export declare namespace SubworkflowNodeDataSerializer {
  type Raw =
    | InlineSubworkflowNodeDataSerializer.Raw
    | DeploymentSubworkflowNodeDataSerializer.Raw;
}

export const InlinePromptNodeDataSerializer: ObjectSchema<
  InlinePromptNodeDataSerializer.Raw,
  Omit<InlinePromptNodeData, "variant">
> = objectSchema({
  label: stringSchema(),
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
    exec_config: PromptVersionExecConfigSerializer.Raw;
    ml_model_name: string;
  }
}

export const DeploymentPromptNodeDataSerializer: ObjectSchema<
  DeploymentPromptNodeDataSerializer.Raw,
  Omit<DeploymentPromptNodeData, "variant">
> = objectSchema({
  label: stringSchema(),
  promptDeploymentId: propertySchema("prompt_deployment_id", stringSchema()),
  releaseTag: propertySchema("release_tag", stringSchema()),
  outputId: propertySchema("output_id", stringSchema()),
  errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  arrayOutputId: propertySchema("array_output_id", stringSchema()),
  sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  targetHandleId: propertySchema("target_handle_id", stringSchema()),
  mlModelFallbacks: propertySchema(
    "ml_model_fallbacks",
    listSchema(stringSchema()).optional()
  ),
});

export declare namespace DeploymentPromptNodeDataSerializer {
  interface Raw {
    prompt_deployment_id: string;
    release_tag: string;
    label: string;
    output_id: string;
    error_output_id?: string | null;
    array_output_id: string;
    source_handle_id: string;
    target_handle_id: string;
    ml_model_fallbacks?: string[] | null;
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
  Omit<LegacyPromptNodeData, "variant">
> = objectSchema({
  label: stringSchema(),
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
> = unionSchema("variant", {
  INLINE: InlinePromptNodeDataSerializer,
  DEPLOYMENT: DeploymentPromptNodeDataSerializer,
  LEGACY: LegacyPromptNodeDataSerializer,
});

export declare namespace PromptNodeDataSerializer {
  type Raw =
    | InlinePromptNodeDataSerializer.Raw
    | DeploymentPromptNodeDataSerializer.Raw
    | LegacyPromptNodeDataSerializer.Raw;
}

export const PromptNodeSerializer: ObjectSchema<
  PromptNodeSerializer.Raw,
  Omit<PromptNode, "type">
> = objectSchema({
  id: stringSchema(),
  data: PromptNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  outputs: listSchema(NodeOutputSerializer).optional(),
  attributes: listSchema(NodeAttributeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace PromptNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    data: PromptNodeDataSerializer.Raw;
  }
}

export const SubworkflowNodeSerializer: ObjectSchema<
  SubworkflowNodeSerializer.Raw,
  Omit<SubworkflowNode, "type">
> = objectSchema({
  id: stringSchema(),
  data: SubworkflowNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace SubworkflowNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    data: SubworkflowNodeDataSerializer.Raw;
  }
}

export const DeploymentMapNodeDataSerializer: ObjectSchema<
  DeploymentMapNodeDataSerializer.Raw,
  Omit<DeploymentMapNodeData, "variant">
> = objectSchema({
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
  Omit<InlineMapNodeData, "variant">
> = objectSchema({
  workflowRawData: propertySchema(
    "workflow_raw_data",
    lazySchema(() => WorkflowRawDataSerializer)
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
> = unionSchema("variant", {
  INLINE: InlineMapNodeDataSerializer,
  DEPLOYMENT: DeploymentMapNodeDataSerializer,
});

export declare namespace MapNodeDataSerializer {
  type Raw =
    | InlineMapNodeDataSerializer.Raw
    | DeploymentMapNodeDataSerializer.Raw;
}

export const MapNodeSerializer: ObjectSchema<
  MapNodeSerializer.Raw,
  Omit<MapNode, "type">
> = objectSchema({
  id: stringSchema(),
  data: MapNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace MapNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    data: MapNodeDataSerializer.Raw;
  }
}

export const GuardrailNodeSerializer: ObjectSchema<
  GuardrailNodeSerializer.Raw,
  Omit<GuardrailNode, "type">
> = objectSchema({
  id: stringSchema(),
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
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace GuardrailNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
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
  repository: stringSchema().optionalNullable(),
});

export declare namespace CodeExecutionPackageSerializer {
  interface Raw {
    version: string;
    name: string;
    repository?: string | null;
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
  Omit<CodeExecutionNode, "type">
> = objectSchema({
  id: stringSchema(),
  data: CodeExecutionNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema("display_data", anySchema().optional()),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace CodeExecutionNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
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
  Omit<SearchNode, "type">
> = objectSchema({
  id: stringSchema(),
  data: SearchNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace SearchNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    data: SearchNodeDataSerializer.Raw;
  }
}

export const ConditionalRuleDataSerializer: ObjectSchema<
  ConditionalRuleDataSerializer.Raw,
  ConditionalRuleData
> = objectSchema({
  id: stringSchema(),
  rules: listSchema(lazySchema(() => ConditionalRuleDataSerializer)).optional(),
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
  Omit<ConditionalNode, "type">
> = objectSchema({
  id: stringSchema(),
  data: ConditionalNodeDataSerializer,
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace ConditionalNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    data: ConditionalNodeDataSerializer.Raw;
  }
}

export const TemplatingNodeSerializer: ObjectSchema<
  TemplatingNodeSerializer.Raw,
  Omit<TemplatingNode, "type">
> = objectSchema({
  id: stringSchema(),
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
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace TemplatingNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
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
  Omit<FinalOutputNode, "type">
> = objectSchema({
  id: stringSchema(),
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
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  outputs: listSchema(NodeOutputSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace FinalOutputNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
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
  Omit<MergeNode, "type">
> = objectSchema({
  id: stringSchema(),
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
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
});

export declare namespace MergeNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
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

export const ApiNodeSerializer: ObjectSchema<
  ApiNodeSerializer.Raw,
  Omit<ApiNode, "type">
> = objectSchema({
  id: stringSchema(),
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
    statusCodeOutputId: propertySchema("status_code_output_id", stringSchema()),
    errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
    targetHandleId: propertySchema("target_handle_id", stringSchema()),
    sourceHandleId: propertySchema("source_handle_id", stringSchema()),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
  attributes: listSchema(NodeAttributeSerializer).optional(),
});

export declare namespace ApiNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
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
  Omit<NoteNode, "type">
> = objectSchema({
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
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace NoteNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
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
  Omit<ErrorNode, "type">
> = objectSchema({
  id: stringSchema(),
  data: objectSchema({
    label: stringSchema(),
    name: stringSchema().optional(),
    targetHandleId: propertySchema("target_handle_id", stringSchema()),
    errorSourceInputId: propertySchema("error_source_input_id", stringSchema()),
    errorOutputId: propertySchema("error_output_id", stringSchema().optional()),
  }),
  inputs: listSchema(NodeInputSerializer),
  displayData: propertySchema(
    "display_data",
    NodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer.optional(),
  definition: CodeResourceDefinitionSerializer.optional(),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  ports: listSchema(NodePortSerializer).optional(),
  trigger: NodeTriggerSerializer.optional(),
});

export declare namespace ErrorNodeSerializer {
  interface Raw extends BaseDisplayableWorkflowNodeSerializer.Raw {
    data: {
      label: string;
      name?: string | null;
      target_handle_id: string;
      error_source_input_id: string;
      error_output_id?: string | null;
    };
  }
}

export const GenericNodeDisplayDataSerializer = objectSchema({
  position: NodeDisplayPositionSerializer.optional(),
  z_index: numberSchema().optional(),
  comment: NodeDisplayCommentSerializer.optional(),
  color: stringSchema().nullable().optional(),
  icon: stringSchema().nullable().optional(),
}) as ObjectSchema<
  GenericNodeDisplayDataSerializer.Raw,
  GenericNodeDisplayData
>;

export declare namespace GenericNodeDisplayDataSerializer {
  interface Raw {
    position?: NodeDisplayPositionSerializer.Raw | null;
    z_index?: number | null;
    comment?: NodeDisplayCommentSerializer.Raw | null;
    color?: string | null;
    icon?: string | null;
  }
}

export const GenericNodeSerializer: ObjectSchema<
  GenericNodeSerializer.Raw,
  Omit<GenericNode, "type">
> = objectSchema({
  id: stringSchema(),
  label: stringSchema(),
  displayData: propertySchema(
    "display_data",
    GenericNodeDisplayDataSerializer.optional()
  ),
  base: CodeResourceDefinitionSerializer,
  definition: CodeResourceDefinitionSerializer.optional(),
  trigger: NodeTriggerSerializer,
  ports: listSchema(NodePortSerializer),
  adornments: listSchema(AdornmentNodeSerializer).optional(),
  attributes: listSchema(NodeAttributeSerializer),
  outputs: listSchema(NodeOutputSerializer),
  should_file_merge: booleanSchema().optional(),
});

export declare namespace GenericNodeSerializer {
  interface Raw extends BaseWorkflowNodeSerializer.Raw {
    id: string;
    label: string;
    base: CodeResourceDefinitionSerializer.Raw;
    display_data?: GenericNodeDisplayDataSerializer.Raw | null;
    definition?: CodeResourceDefinitionSerializer.Raw | null;
    trigger: NodeTriggerSerializer.Raw;
    ports: NodePortSerializer.Raw[];
    adornments?: AdornmentNodeSerializer.Raw[] | null;
    attributes: NodeAttributeSerializer.Raw[];
    outputs: NodeOutputSerializer.Raw[];
  }
}

export const WorkflowNodeSerializer: Schema<
  WorkflowNodeSerializer.Raw,
  WorkflowNode
> = unionSchema("type", {
  ENTRYPOINT: EntrypointNodeSerializer,
  PROMPT: PromptNodeSerializer,
  SEARCH: SearchNodeSerializer,
  SUBWORKFLOW: SubworkflowNodeSerializer,
  MAP: MapNodeSerializer,
  METRIC: GuardrailNodeSerializer,
  CODE_EXECUTION: CodeExecutionNodeSerializer,
  TERMINAL: FinalOutputNodeSerializer,
  MERGE: MergeNodeSerializer,
  TEMPLATING: TemplatingNodeSerializer,
  CONDITIONAL: ConditionalNodeSerializer,
  API: ApiNodeSerializer,
  NOTE: NoteNodeSerializer,
  ERROR: ErrorNodeSerializer,
  GENERIC: GenericNodeSerializer,
});

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
  display_data: propertySchema(
    "display_data",
    WorkflowEdgeDisplayDataSerializer.optional()
  ),
});

export declare namespace WorkflowEdgeSerializer {
  interface Raw {
    id: string;
    type: "DEFAULT";
    source_node_id: string;
    source_handle_id: string;
    target_node_id: string;
    target_handle_id: string;
    display_data?: WorkflowEdgeDisplayDataSerializer.Raw | null;
  }
}

export declare namespace WorkflowOutputValueSerializer {
  interface Raw {
    output_variable_id: string;
    value?: WorkflowValueDescriptorSerializer.Raw | null;
  }
}

export const WorkflowOutputValueSerializer: ObjectSchema<
  WorkflowOutputValueSerializer.Raw,
  WorkflowOutputValue
> = objectSchema({
  outputVariableId: propertySchema("output_variable_id", stringSchema()),
  value: WorkflowValueDescriptorSerializer.optional(),
});

export const WorkflowTriggerSerializer: ObjectSchema<
  WorkflowTriggerSerializer.Raw,
  WorkflowTrigger
> = objectSchema({
  id: stringSchema(),
  type: stringSchema(),
  attributes: listSchema(NodeAttributeSerializer),
});

export declare namespace WorkflowTriggerSerializer {
  interface Raw {
    id: string;
    type: string;
    attributes: NodeAttributeSerializer.Raw[];
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
  outputValues: propertySchema(
    "output_values",
    listSchema(WorkflowOutputValueSerializer).optional()
  ),
});

export declare namespace WorkflowRawDataSerializer {
  interface Raw {
    nodes: WorkflowNodeSerializer.Raw[];
    edges: WorkflowEdgeSerializer.Raw[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    display_data?: any;
    definition?: CodeResourceDefinitionSerializer.Raw | null;
    output_values?: WorkflowOutputValueSerializer.Raw[] | null;
  }
}

export const ModuleDataSerializer = objectSchema({
  additionalFiles: propertySchema(
    "additional_files",
    recordSchema(stringSchema(), stringSchema()).optional()
  ),
});

export declare namespace ModuleDataSerializer {
  interface Raw {
    additional_files?: Record<string, string>;
  }
}

export const WorkflowVersionExecConfigSerializer = objectSchema({
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
  stateVariables: propertySchema(
    "state_variables",
    listSchema(VellumVariableSerializer).optional()
  ),
  runnerConfig: propertySchema(
    "runner_config",
    objectSchema({
      containerImageName: propertySchema(
        "container_image_name",
        stringSchema().optional()
      ),
      containerImageTag: propertySchema(
        "container_image_tag",
        stringSchema().optional()
      ),
    }).optional()
  ),
  moduleData: propertySchema("module_data", ModuleDataSerializer.optional()),
  triggers: listSchema(WorkflowTriggerSerializer).optional(),
});

export declare namespace WorkflowVersionExecConfigSerializer {
  interface Raw {
    workflow_raw_data: WorkflowRawDataSerializer.Raw;
    input_variables: VellumVariableSerializer.Raw[];
    state_variables?: VellumVariableSerializer.Raw[] | null;
    output_variables: VellumVariableSerializer.Raw[];
    runner_config?: {
      container_image_name?: string | null;
      container_image_tag?: string | null;
    } | null;
    module_data?: ModuleDataSerializer.Raw | null;
    triggers?: WorkflowTriggerSerializer.Raw[] | null;
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
  display_data: propertySchema(
    "display_data",
    WorkflowEdgeDisplayDataSerializer.optional()
  ),
});

export declare namespace WorkflowEdgeSerializer {
  interface Raw {
    id: string;
    source_node_id: string;
    source_handle_id: string;
    target_node_id: string;
    target_handle_id: string;
    display_data?: WorkflowEdgeDisplayDataSerializer.Raw | null;
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
