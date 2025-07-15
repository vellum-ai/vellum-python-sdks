import { v4 as uuidv4 } from "uuid";
import {
  CodeResourceDefinition,
  PromptParameters,
  PromptSettings,
  VellumVariable,
  VellumVariableType,
} from "vellum-ai/api";

import { edgesFactory } from "./edge-data-factories";

import { NodeDataFactoryBuilder } from "src/__test__/helpers/node-data-factory-builder";
import { VellumValueLogicalExpressionSerializer } from "src/serializers/vellum";
import {
  AdornmentNode,
  ApiNode,
  CodeExecutionNode,
  CodeExecutionPackage,
  ConditionalNode,
  ConditionalNodeConditionData,
  ConstantValuePointer,
  EntrypointNode,
  ErrorNode,
  FinalOutputNode,
  GenericNode,
  GuardrailNode,
  MapNode,
  MergeNode,
  NodeAttribute,
  NodeInput,
  NodeInputValuePointerRule,
  NodeOutput,
  NodeOutputData,
  NodePort,
  NodeTrigger,
  NoteNode,
  PromptNode,
  PromptTemplateBlock,
  SearchNode,
  SubworkflowNode,
  TemplatingNode,
  VellumLogicalConditionGroup,
  WorkflowDataNode,
  WorkflowNodeType,
} from "src/types/vellum";

export function entrypointNodeDataFactory(): EntrypointNode {
  return {
    id: "entrypoint",
    type: WorkflowNodeType.ENTRYPOINT,
    inputs: [],
    data: { label: "Entrypoint", sourceHandleId: "<source_handle_id>" },
  };
}

export const nodeInputFactory = (
  props: Omit<Partial<NodeInput>, "value"> & {
    value: NodeInputValuePointerRule | NodeInputValuePointerRule[];
  }
): NodeInput => ({
  id: props.id ?? uuidv4(),
  key: props.key ?? "input",
  value: {
    combinator: "OR",
    rules: Array.isArray(props.value) ? props.value : [props.value],
  },
});

export function terminalNodeDataFactory(): FinalOutputNode {
  return {
    id: "terminal-node-1",
    type: WorkflowNodeType.TERMINAL,
    inputs: [
      {
        id: "node-input-id",
        key: "query",
        value: {
          combinator: "OR",
          rules: [
            {
              type: "INPUT_VARIABLE",
              data: {
                inputVariableId: "input-variable-id",
              },
            },
          ],
        },
      },
    ],
    data: {
      label: "Final Output",
      name: "query",
      targetHandleId: "target-handle-id",
      outputId: "output-id",
      outputType: "STRING",
      nodeInputId: "node-input-id",
    },
  };
}

export function mergeNodeDataFactory(
  numTargetHandles: number = 2
): NodeDataFactoryBuilder<MergeNode> {
  const nodeData: MergeNode = {
    id: "merge-node-1",
    type: WorkflowNodeType.MERGE,
    inputs: [],
    data: {
      label: "Merge Node",
      mergeStrategy: "AWAIT_ALL",
      targetHandles: Array.from({ length: numTargetHandles }, (_, index) => ({
        id: `target-handle-id-${index + 1}`,
      })),
      sourceHandleId: "source-handle-id",
    },
  };
  return new NodeDataFactoryBuilder<MergeNode>(nodeData);
}

export function searchNodeDataFactory(args?: {
  metadataFiltersNodeInputId?: string;
  metadataFilters?: VellumLogicalConditionGroup;
  metadataFilterInputs?: NodeInput[];
  errorOutputId?: string;
  limitInput?: ConstantValuePointer;
  queryInput?: NodeInput;
  includeDocumentIndexInput?: boolean;
}): NodeDataFactoryBuilder<SearchNode> {
  const errorOutputId = args?.errorOutputId;
  const includeDocumentIndexInput = args?.includeDocumentIndexInput ?? true;

  const metadataFiltersNodeInputId =
    args?.metadataFiltersNodeInputId ?? "7c43b315-d1f2-4727-9540-6cc3fd4641f3";
  const metadataFilters = args?.metadataFilters ?? {
    type: "LOGICAL_CONDITION_GROUP",
    negated: false,
    combinator: "AND",
    conditions: [
      {
        type: "LOGICAL_CONDITION_GROUP",
        negated: false,
        combinator: "AND",
        conditions: [
          {
            type: "LOGICAL_CONDITION",
            operator: "=",
            lhsVariableId: "a6322ca2-8b65-4d26-b3a1-f926dcada0fa",
            rhsVariableId: "c539a2e2-0873-43b0-ae21-81790bb1c4cb",
          },
        ],
      },
    ],
  };
  const metadataFilterInputs: NodeInput[] = args?.metadataFilterInputs ?? [
    {
      id: "a6322ca2-8b65-4d26-b3a1-f926dcada0fa",
      key: "vellum-query-builder-variable-a6322ca2-8b65-4d26-b3a1-f926dcada0fa",
      value: {
        rules: [
          {
            type: "INPUT_VARIABLE",
            data: {
              inputVariableId: "c95cccdc-8881-4528-bc63-97d9df6e1d87",
            },
          },
        ],
        combinator: "OR",
      },
    },
    {
      id: "c539a2e2-0873-43b0-ae21-81790bb1c4cb",
      key: "vellum-query-builder-variable-c539a2e2-0873-43b0-ae21-81790bb1c4cb",
      value: {
        rules: [
          {
            type: "INPUT_VARIABLE",
            data: {
              inputVariableId: "c95cccdc-8881-4528-bc63-97d9df6e1d87",
            },
          },
        ],
        combinator: "OR",
      },
    },
  ];

  const queryInput = args?.queryInput ?? {
    id: "f3a0d8b9-7772-4db6-8e28-f49f8c4d9e2a",
    key: "query",
    value: {
      rules: [
        {
          type: "INPUT_VARIABLE",
          data: {
            inputVariableId: "a6ef8809-346e-469c-beed-2e5c4e9844c5",
          },
        },
      ],
      combinator: "OR",
    },
  };

  const nodeData: SearchNode = {
    id: "search",
    type: WorkflowNodeType.SEARCH,
    data: {
      label: "Search Node",
      sourceHandleId: "e4dedb66-0638-4f0c-9941-6420bfe353b2",
      targetHandleId: "370d712d-3369-424e-bcf7-f4da1aef3928",
      errorOutputId,
      resultsOutputId: "77839b3c-fe1c-4dcb-9c61-2fac827f729b",
      textOutputId: "d56d7c49-7b45-4933-9779-2bd7f82c2141",
      queryNodeInputId: queryInput.id,
      documentIndexNodeInputId: "b49bc1ab-2ad5-4cf2-8966-5cc87949900d",
      weightsNodeInputId: "1daf3180-4b92-472a-8665-a7703c84a94e",
      limitNodeInputId: "161d264e-d04e-4c37-8e50-8bbb4c90c46e",
      separatorNodeInputId: "4eddefc0-90d5-422a-aec2-bc94c8f1d83c",
      resultMergingEnabledNodeInputId: "dc9f880b-81bc-4644-b025-8f7d5db23a48",
      externalIdFiltersNodeInputId: "61933e79-b0c2-4e3c-bf07-e2d93b9d9c54",
      metadataFiltersNodeInputId,
    },
    inputs: [
      queryInput,
      ...(includeDocumentIndexInput
        ? [
            {
              id: "b49bc1ab-2ad5-4cf2-8966-5cc87949900d",
              key: "document_index_id",
              value: {
                combinator: "OR" as const,
                rules: [
                  {
                    type: "CONSTANT_VALUE" as const,
                    data: {
                      type: "STRING" as const,
                      value: "d5beca61-aacb-4b22-a70c-776a1e025aa4",
                    },
                  },
                ],
              },
            },
          ]
        : []),
      {
        id: "1daf3180-4b92-472a-8665-a7703c84a94e",
        key: "weights",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "JSON",
                value: {
                  semantic_similarity: 0.8,
                  keywords: 0.2,
                },
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: "161d264e-d04e-4c37-8e50-8bbb4c90c46e",
        key: "limit",
        value: {
          rules: [
            args?.limitInput ?? {
              type: "CONSTANT_VALUE",
              data: {
                type: "NUMBER",
                value: 8,
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: "4eddefc0-90d5-422a-aec2-bc94c8f1d83c",
        key: "separator",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "\n\n#####\n\n",
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: "dc9f880b-81bc-4644-b025-8f7d5db23a48",
        key: "result_merging_enabled",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "True",
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: "61933e79-b0c2-4e3c-bf07-e2d93b9d9c54",
        key: "external_id_filters",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "JSON",
                value: null,
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: metadataFiltersNodeInputId,
        key: "metadata_filters",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "JSON",
                value:
                  VellumValueLogicalExpressionSerializer.jsonOrThrow(
                    metadataFilters
                  ),
              },
            },
          ],
          combinator: "OR",
        },
      },
      ...metadataFilterInputs,
    ],
  };

  return new NodeDataFactoryBuilder<SearchNode>(nodeData);
}

export function noteNodeDataFactory(): NodeDataFactoryBuilder<NoteNode> {
  const nodeData: NoteNode = {
    id: "<note-node-id>",
    type: WorkflowNodeType.NOTE,
    inputs: [],
    data: {
      label: "Note Node",
      text: "This is a note",
      style: {
        color: "red",
        fontSize: 12,
        fontWeight: "bold",
      },
    },
  };
  return new NodeDataFactoryBuilder<NoteNode>(nodeData);
}

export function guardrailNodeDataFactory({
  errorOutputId,
  inputs,
}: {
  errorOutputId?: string;
  inputs?: NodeInput[];
} = {}): NodeDataFactoryBuilder<GuardrailNode> {
  const nodeData: GuardrailNode = {
    id: "metric",
    type: WorkflowNodeType.METRIC,
    data: {
      label: "Guardrail Node",
      sourceHandleId: "92aafe31-101b-47d3-86f2-e261c7747c16",
      targetHandleId: "1817fbab-db21-4219-8b34-0e150ce78887",
      errorOutputId,
      metricDefinitionId: "589df5bd-8c0d-4797-9a84-9598ecd043de",
      releaseTag: "LATEST",
    },
    inputs: inputs ?? [],
  };
  return new NodeDataFactoryBuilder<GuardrailNode>(nodeData);
}

const generateBlockGivenType = (blockType: string): PromptTemplateBlock => {
  if (blockType === "JINJA") {
    return {
      id: "block-id",
      blockType: "JINJA",
      properties: {
        template: "Summarize what this means {{ INPUT_VARIABLE }}",
      },
      state: "ENABLED",
    };
  } else if (blockType === "CHAT_MESSAGE") {
    return {
      id: "block-id",
      blockType: "CHAT_MESSAGE",
      properties: {
        blocks: [
          {
            id: "block-id",
            blockType: "RICH_TEXT",
            blocks: [
              {
                id: "block-id",
                blockType: "PLAIN_TEXT",
                text: "Summarize the following text:\n\n",
                state: "ENABLED",
              },
              {
                id: "block-id",
                blockType: "VARIABLE",
                state: "ENABLED",
                inputVariableId: "text",
              },
            ],
            state: "ENABLED",
          },
        ],
        chatRole: "SYSTEM",
        chatMessageUnterminated: false,
      },
      state: "ENABLED",
    };
  } else if (blockType === "VARIABLE") {
    return {
      id: "block-id",
      blockType: "VARIABLE",
      state: "ENABLED",
      inputVariableId: "text",
    };
  } else if (blockType === "RICH_TEXT") {
    return {
      id: "block-id",
      blockType: "RICH_TEXT",
      blocks: [
        {
          id: "block-id",
          blockType: "PLAIN_TEXT",
          text: "Hello World!",
          state: "ENABLED",
        },
      ],
      state: "ENABLED",
    };
  } else if (blockType === "FUNCTION_DEFINITION") {
    return {
      id: "block-id",
      blockType: "FUNCTION_DEFINITION",
      properties: {
        functionName: "functionTest",
        functionDescription: "This is a test function",
      },
      state: "ENABLED",
    };
  } else {
    throw new Error("Unrecognized block type");
  }
};

export function inlinePromptNodeDataInlineVariantFactory({
  blockType,
  errorOutputId,
  parameters,
  defaultBlock,
  settings,
  inputs,
  attributes,
}: {
  blockType?: string;
  errorOutputId?: string;
  parameters?: PromptParameters;
  defaultBlock?: PromptTemplateBlock;
  settings?: PromptSettings;
  inputs?: NodeInput[];
  attributes?: NodeAttribute[];
} = {}): NodeDataFactoryBuilder<PromptNode> {
  const block = defaultBlock ?? generateBlockGivenType(blockType ?? "JINJA");
  const nodeData: PromptNode = {
    id: "7e09927b-6d6f-4829-92c9-54e66bdcaf80",
    type: WorkflowNodeType.PROMPT,
    data: {
      variant: "INLINE",
      label: "Prompt Node",
      outputId: "2d4f1826-de75-499a-8f84-0a690c8136ad",
      arrayOutputId: "771c6fba-5b4a-4092-9d52-693242d7b92c",
      errorOutputId,
      sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb98",
      targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2948",
      execConfig: {
        parameters: parameters ?? {
          temperature: 0.0,
          maxTokens: 1000,
          topP: 1.0,
          topK: 0,
          frequencyPenalty: 0.0,
          presencePenalty: 0.0,
          logitBias: {},
          customParameters: {},
        },
        inputVariables: [
          {
            id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
            key: "text",
            type: "STRING",
          },
        ],
        promptTemplateBlockData: {
          blocks: [block],
          version: 1,
        },
        settings: settings,
      },
      mlModelName: "gpt-4o-mini",
    },
    inputs: inputs ?? [
      {
        id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
        key: "text",
        value: {
          rules: [
            {
              type: "INPUT_VARIABLE",
              data: {
                inputVariableId: "90c6afd3-06cc-430d-aed1-35937c062531",
              },
            },
          ],
          combinator: "OR",
        },
      },
    ],
    attributes,
  };
  return new NodeDataFactoryBuilder<PromptNode>(nodeData);
}

export function inlinePromptNodeDataLegacyVariantFactory({
  blockType,
  errorOutputId,
}: {
  blockType: string;
  errorOutputId?: string;
}): PromptNode {
  const block = generateBlockGivenType(blockType);
  const nodeData: PromptNode = {
    id: "7e09927b-6d6f-4829-92c9-54e66bdcaf80",
    type: WorkflowNodeType.PROMPT,
    data: {
      variant: "LEGACY",
      label: "Prompt Node",
      outputId: "2d4f1826-de75-499a-8f84-0a690c8136ad",
      arrayOutputId: "771c6fba-5b4a-4092-9d52-693242d7b92c",
      errorOutputId,
      sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb98",
      targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2948",
      sandboxRoutingConfig: {
        version: 1,
        promptVersionData: {
          execConfig: {
            parameters: {
              temperature: 0.0,
              maxTokens: 1000,
              topP: 1.0,
              topK: 0,
              frequencyPenalty: 0.0,
              presencePenalty: 0.0,
              logitBias: {},
              customParameters: {},
            },
            inputVariables: [
              {
                id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
                key: "text",
                type: "STRING",
              },
            ],
            promptTemplateBlockData: {
              blocks: [block],
              version: 1,
            },
          },
          mlModelToWorkspaceId: "gpt-4o-mini",
        },
      },
    },
    inputs: [
      {
        id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
        key: "text",
        value: {
          rules: [
            {
              type: "INPUT_VARIABLE",
              data: {
                inputVariableId: "90c6afd3-06cc-430d-aed1-35937c062531",
              },
            },
          ],
          combinator: "OR",
        },
      },
    ],
  };
  return nodeData;
}

export function promptDeploymentNodeDataFactory({
  errorOutputId = undefined,
  mlModelFallbacks,
  inputs,
}: {
  errorOutputId?: string;
  mlModelFallbacks?: string[];
  inputs?: NodeInput[];
} = {}): NodeDataFactoryBuilder<PromptNode> {
  const nodeData: PromptNode = {
    id: "947cc337-9a53-4c12-9a38-4f65c04c6317",
    type: "PROMPT",
    data: {
      variant: "DEPLOYMENT",
      label: "Prompt Deployment Node",
      outputId: "fa015382-7e5b-404e-b073-1c5f01832169",
      arrayOutputId: "4d257095-e908-4fc3-8159-a6ac0018e1f1",
      errorOutputId: errorOutputId,
      sourceHandleId: "1539a6ed-6bf9-43a5-9e4a-f82ec5615ee3",
      targetHandleId: "e1f8a351-ab12-4167-93ee-d2dd72c8d15c",
      promptDeploymentId: "afd05488-7a25-4ff2-b87b-878e9552474e",
      releaseTag: "LATEST",
      mlModelFallbacks,
    },
    inputs: inputs ?? [
      {
        id: "3911bd2e-eaaf-4805-9ffc-e5d6a71c91a7",
        key: "my_var_1",
        value: {
          rules: [],
          combinator: "OR",
        },
      },
    ],
    displayData: {
      width: 480,
      height: 170,
      position: {
        x: 2470.8372576177285,
        y: 219.71887984764544,
      },
    },
    definition: undefined,
  };
  return new NodeDataFactoryBuilder<PromptNode>(nodeData);
}

export function templatingNodeFactory({
  id,
  outputId,
  label,
  sourceHandleId,
  targetHandleId,
  errorOutputId,
  outputType = VellumVariableType.String,
  templateNodeInputId,
  inputs,
  template,
}: {
  id?: string;
  outputId?: string;
  label?: string;
  sourceHandleId?: string;
  targetHandleId?: string;
  errorOutputId?: string;
  outputType?: VellumVariableType;
  templateNodeInputId?: string;
  inputs?: NodeInput[];
  template?: ConstantValuePointer;
} = {}): NodeDataFactoryBuilder<TemplatingNode> {
  const defaultTemplate: ConstantValuePointer = {
    type: "CONSTANT_VALUE",
    data: {
      type: "STRING",
      value: "Hello, World!",
    },
  };

  const nodeInputs: NodeInput[] = inputs ?? [];

  const templateInputExists = nodeInputs.some(
    (input) => input.key === "template"
  );
  if (!templateInputExists) {
    nodeInputs.push({
      id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
      key: "template",
      value: {
        rules: [template ?? defaultTemplate],
        combinator: "OR",
      },
    });
  }

  const nodeData: TemplatingNode = {
    id: id ?? "46e221ab-a749-41a2-9242-b1f5bf31f3a5",
    type: WorkflowNodeType.TEMPLATING,
    data: {
      label: label ?? "Templating Node",
      outputId: outputId ?? "2d4f1826-de75-499a-8f84-0a690c8136ad",
      errorOutputId,
      sourceHandleId: sourceHandleId ?? "6ee2c814-d0a5-4ec9-83b6-45156e2f22c4",
      targetHandleId: targetHandleId ?? "3960c8e1-9baa-4b9c-991d-e399d16a45aa",
      templateNodeInputId:
        templateNodeInputId ?? "7b8af68b-cf60-4fca-9c57-868042b5b616",
      outputType: outputType,
    },
    inputs: nodeInputs,
  };
  return new NodeDataFactoryBuilder<TemplatingNode>(nodeData);
}

export function subworkflowDeploymentNodeDataFactory(): NodeDataFactoryBuilder<SubworkflowNode> {
  const nodeData: SubworkflowNode = {
    id: "c8f2964c-09b8-44e0-a06d-606319fe5e2a",
    type: "SUBWORKFLOW",
    data: {
      label: "Subworkflow Node",
      sourceHandleId: "600efd51-8677-4ba3-a582-b298bebb2868",
      targetHandleId: "f5e6bd33-527a-4ba6-8906-cd5e96a4321c",
      errorOutputId: undefined,
      variant: "DEPLOYMENT",
      workflowDeploymentId: "58171df8-cdf9-4d10-a9ed-22eaf545b22a",
      releaseTag: "LATEST",
    },
    inputs: [
      {
        id: "f62b7511-dd69-4dff-a4fc-718a9db3ceba",
        key: "input",
        value: {
          rules: [],
          combinator: "OR",
        },
      },
    ],
    displayData: {
      position: {
        x: 2239.986322714681,
        y: 484.74458968144046,
      },
    },
    definition: undefined,
  };
  return new NodeDataFactoryBuilder<SubworkflowNode>(nodeData);
}

export function conditionalNodeWithNullOperatorFactory({
  id,
  nodeOutputReference,
}: {
  nodeOutputReference: NodeOutputData;
  id?: string;
}): ConditionalNode {
  const nodeData: ConditionalNode = {
    id: id ?? "b81a4453-7b80-41ea-bd55-c62df8878fd3",
    type: WorkflowNodeType.CONDITIONAL,
    data: {
      label: "Conditional Node",
      targetHandleId: "842b9dda-7977-47ad-a322-eb15b4c7069d",
      conditions: [
        {
          id: "8d0d8b56-6c17-4684-9f16-45dd6ce23060",
          type: "IF",
          sourceHandleId: "63345ab5-1a4d-48a1-ad33-91bec41f92a5",
          data: {
            id: "fa50fb0c-8d62-40e3-bd88-080b52efd4b2",
            rules: [
              {
                id: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc",
                rules: [],
                fieldNodeInputId: "2cb6582e-c329-4952-8598-097830b766c7",
                operator: "null",
              },
              {
                id: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cd",
                rules: [],
                fieldNodeInputId: "2cb6582e-c329-4952-8598-097830b766c8",
                operator: "null",
              },
            ],
            combinator: "AND",
          },
        },
      ],
      version: "2",
    },
    inputs: [
      {
        id: "2cb6582e-c329-4952-8598-097830b766c7",
        key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.field",
        value: {
          rules: [
            {
              type: "INPUT_VARIABLE",
              data: {
                inputVariableId: "d2287fee-98fb-421c-9464-e54d8f70f046",
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: "2cb6582e-c329-4952-8598-097830b766c8",
        key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cd.field",
        value: {
          rules: [
            {
              type: "NODE_OUTPUT",
              data: nodeOutputReference,
            },
          ],
          combinator: "OR",
        },
      },
    ],
    displayData: {
      width: 480,
      height: 180,
      position: {
        x: 2247.2797390213086,
        y: 30.917121251477084,
      },
    },
  };
  return nodeData;
}

export function conditionalNodeFactory({
  id,
  label,
  targetHandleId,
  ifSourceHandleId,
  elseSourceHandleId,
  inputReferenceId,
  inputReferenceNodeId,
  inputs,
  includeElif = false,
  conditions = null,
}: {
  id?: string;
  label?: string;
  targetHandleId?: string;
  ifSourceHandleId?: string;
  elseSourceHandleId?: string;
  inputReferenceId?: string;
  inputReferenceNodeId?: string;
  includeElif?: boolean;
  conditions?: ConditionalNodeConditionData[] | null;
  inputs?: NodeInput[];
} = {}): NodeDataFactoryBuilder<ConditionalNode> {
  // Some test may want to pass in conditions directly
  if (!conditions) {
    conditions = [
      {
        id: "8d0d8b56-6c17-4684-9f16-45dd6ce23060",
        type: "IF",
        sourceHandleId:
          ifSourceHandleId ?? "63345ab5-1a4d-48a1-ad33-91bec41f92a5",
        data: {
          id: "fa50fb0c-8d62-40e3-bd88-080b52efd4b2",
          rules: [
            {
              id: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc",
              rules: [],
              fieldNodeInputId: "2cb6582e-c329-4952-8598-097830b766c7",
              operator: "=",
              valueNodeInputId: "cf63d0ad-5e52-4031-a29f-922e7004cdd8",
            },
          ],
          combinator: "AND",
        },
      },
    ];
  }

  if (includeElif) {
    conditions.push({
      id: "e63c3933-ef86-451f-88bc-d7ea7dce4310",
      type: "ELIF",
      sourceHandleId: "2c03f27f-ea64-42fc-8a6c-383550c58ae4",
      data: {
        id: "fa50fb0c-8d62-40e3-bd88-080b52efd4b2",
        rules: [
          {
            id: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc",
            rules: [],
            fieldNodeInputId: "2cb6582e-c329-4952-8598-097830b766c7",
            operator: "notNull",
          },
        ],
        combinator: "AND",
      },
    });
  }
  conditions.push({
    id: "ea63ccd5-3fe3-4371-ba3c-6d3ec7ca2b60",
    type: "ELSE",
    sourceHandleId:
      elseSourceHandleId ?? "14a8b603-6039-4491-92d4-868a4dae4c15",
  });
  const nodeData: ConditionalNode = {
    id: id ?? "b81a4453-7b80-41ea-bd55-c62df8878fd3",
    type: WorkflowNodeType.CONDITIONAL,
    data: {
      label: label ?? "Conditional Node",
      targetHandleId: targetHandleId ?? "842b9dda-7977-47ad-a322-eb15b4c7069d",
      conditions: conditions,
      version: "2",
    },
    inputs: inputs
      ? inputs
      : inputReferenceId && inputReferenceNodeId
      ? [
          {
            id: "2cb6582e-c329-4952-8598-097830b766c7",
            key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.field",
            value: {
              rules: [
                {
                  type: "NODE_OUTPUT",
                  data: {
                    nodeId: inputReferenceNodeId,
                    outputId: inputReferenceId,
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "cf63d0ad-5e52-4031-a29f-922e7004cdd8",
            key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.value",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "testtest",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ]
      : [
          {
            id: "2cb6582e-c329-4952-8598-097830b766c7",
            key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.field",
            value: {
              rules: [
                {
                  type: "INPUT_VARIABLE",
                  data: {
                    inputVariableId: "d2287fee-98fb-421c-9464-e54d8f70f046",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "cf63d0ad-5e52-4031-a29f-922e7004cdd8",
            key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.value",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "testtest",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
    displayData: {
      width: 480,
      height: 180,
      position: {
        x: 2247.2797390213086,
        y: 30.917121251477084,
      },
    },
  };
  return new NodeDataFactoryBuilder<ConditionalNode>(nodeData);
}

export interface ApiNodeFactoryProps {
  errorOutputId?: string;
  bearerToken?: NodeInput;
  apiKeyHeaderValue?: NodeInput;
  additionalHeaders?: { key: NodeInput; value: NodeInput }[];
  authorizationTypeInput?: NodeInput | null;
  url?: string | null;
  method?: string;
  body?: Record<string, unknown> | null;
  statusCodeOutputId?: string;
  id?: string;
}

export function apiNodeFactory({
  id,
  statusCodeOutputId,
  errorOutputId,
  bearerToken,
  apiKeyHeaderValue,
  additionalHeaders,
  authorizationTypeInput,
  url = "https://example.vellum.ai",
  method = "POST",
  body = {},
}: ApiNodeFactoryProps = {}): NodeDataFactoryBuilder<ApiNode> {
  const bearerTokenInput = bearerToken ?? {
    id: "931502c1-23a5-4e2a-a75e-80736c42f3c9",
    key: "bearer_token_value",
    value: {
      rules: [
        {
          type: "CONSTANT_VALUE",
          data: {
            type: "STRING",
            value: "<my-bearer-token>",
          },
        },
      ],
      combinator: "OR",
    },
  };

  const apiKeyHeaderValueInput = apiKeyHeaderValue ?? {
    id: "bfc2e790-66fd-42fd-acf7-3b2c785c1a0a",
    key: "api_key_header_value",
    value: {
      rules: [
        {
          type: "CONSTANT_VALUE",
          data: {
            type: "STRING",
            value: "<my-api-value>",
          },
        },
      ],
      combinator: "OR",
    },
  };

  const additionalHeaderInputs =
    additionalHeaders ??
    ([
      {
        key: {
          id: "8ad006f3-d19e-4af1-931f-3e955152cd91",
          key: "additional_header_key_1",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "foo",
                },
              },
            ],
            combinator: "OR",
          },
        },
        value: {
          id: "36865dca-40b4-432c-bab4-1e11bb9f4083",
          key: "additional_header_value_1",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "foo-value",
                },
              },
            ],
            combinator: "OR",
          },
        },
      },
      {
        key: {
          id: "3075be8c-248b-421d-9266-7779297be883",
          key: "additional_header_key_2",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "bar",
                },
              },
            ],
            combinator: "OR",
          },
        },
        value: {
          id: "00baaee1-b785-403d-b391-f68b3aea334f",
          key: "additional_header_value_2",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "bar-value",
                },
              },
            ],
            combinator: "OR",
          },
        },
      },
      {
        key: {
          id: "13c2dd5e-cdd0-431b-aa91-46ad8da1cb51",
          key: "additional_header_key_3",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "baz",
                },
              },
            ],
            combinator: "OR",
          },
        },
        value: {
          id: "408c2b3d-7c30-4e01-a2e3-276753beadbc",
          key: "additional_header_value_3",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "baz-value",
                },
              },
            ],
            combinator: "OR",
          },
        },
      },
    ] as { key: NodeInput; value: NodeInput }[]);

  const defaultAuthorizationTypeInput: NodeInput = {
    id: "de330dac-05b1-4e78-bee7-7452203af3d5",
    key: "authorization_type",
    value: {
      rules: [
        {
          type: "CONSTANT_VALUE" as const,
          data: {
            type: "STRING" as const,
            value: "API_KEY",
          },
        },
      ],
      combinator: "OR",
    },
  };

  const inputs: NodeInput[] = [
    {
      id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
      key: "method",
      value: {
        rules: [
          {
            type: "CONSTANT_VALUE" as const,
            data: {
              type: "STRING" as const,
              value: method,
            },
          },
        ],
        combinator: "OR",
      },
    },
    ...(url
      ? [
          {
            id: "480a4c12-22d6-4223-a38a-85db5eda118c",
            key: "url",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE" as const,
                  data: {
                    type: "STRING" as const,
                    value: url,
                  },
                },
              ],
              combinator: "OR" as const,
            },
          },
        ]
      : []),
    {
      id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
      key: "body",
      value: {
        rules: [
          {
            type: "CONSTANT_VALUE",
            data: {
              type: "JSON",
              value: body,
            },
          },
        ],
        combinator: "OR",
      },
    },
    ...(authorizationTypeInput !== null
      ? [authorizationTypeInput ?? defaultAuthorizationTypeInput]
      : []),
    bearerTokenInput,
    {
      id: "96c8343d-cc94-4df0-9001-eb2905a00be7",
      key: "api_key_header_key",
      value: {
        rules: [
          {
            type: "CONSTANT_VALUE",
            data: {
              type: "STRING",
            },
          },
        ],
        combinator: "OR",
      },
    },
    apiKeyHeaderValueInput,
    ...additionalHeaderInputs.flatMap(({ key, value }) => [key, value]),
  ];

  const nodeData: ApiNode = {
    id: id ?? "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
    type: "API",
    data: {
      label: "API Node",
      methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
      urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
      bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
      authorizationTypeInputId:
        authorizationTypeInput === null
          ? undefined
          : authorizationTypeInput?.id ?? defaultAuthorizationTypeInput.id,
      bearerTokenValueInputId: bearerTokenInput.id,
      apiKeyHeaderKeyInputId: "96c8343d-cc94-4df0-9001-eb2905a00be7",
      apiKeyHeaderValueInputId: apiKeyHeaderValueInput.id,
      additionalHeaders: additionalHeaderInputs.map(({ key, value }) => ({
        headerKeyInputId: key.id,
        headerValueInputId: value.id,
      })),
      textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
      jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
      statusCodeOutputId:
        statusCodeOutputId ?? "69250713-617d-42a4-9326-456c70d0ef20",
      errorOutputId,
      targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
      sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
    },
    inputs: inputs,
    displayData: {
      width: 462,
      height: 288,
      position: {
        x: 2075.7067885117494,
        y: 234.65663468515768,
      },
    },
  };
  return new NodeDataFactoryBuilder<ApiNode>(nodeData);
}

export function codeExecutionNodeFactory({
  id,
  outputId,
  label,
  codeInputValueRule,
  codeOutputValueType,
  runtimeInput,
  generateLogOutputId = true,
  code,
  packages,
}: {
  id?: string;
  outputId?: string;
  label?: string;
  codeInputValueRule?: NodeInputValuePointerRule;
  codeOutputValueType?: VellumVariableType;
  runtimeInput?: NodeInput;
  generateLogOutputId?: boolean;
  code?: string;
  packages?: CodeExecutionPackage[];
} = {}): NodeDataFactoryBuilder<CodeExecutionNode> {
  const runtime =
    runtimeInput ??
    ({
      id: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
      key: "runtime",
      value: {
        combinator: "OR",
        rules: [
          {
            type: "CONSTANT_VALUE",
            data: {
              type: "STRING",
              value: "PYTHON_3_11_6",
            },
          },
        ],
      },
    } as NodeInput);

  const nodeData: CodeExecutionNode = {
    id: id ?? "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
    type: "CODE_EXECUTION",
    data: {
      label: label ?? "Code Execution Node",
      codeInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
      outputId: outputId ?? "81b270c0-4deb-4db3-aae5-138f79531b2b",
      outputType: codeOutputValueType ?? "STRING",
      logOutputId: generateLogOutputId
        ? "46abb839-400b-4766-997e-9c463b526139"
        : undefined,
      runtimeInputId: runtime.id,
      targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
      sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
      packages: packages,
    },
    inputs: [
      {
        id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
        key: "code",
        value: {
          combinator: "OR",
          rules: codeInputValueRule
            ? [codeInputValueRule]
            : [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: code ?? "print('Hello, World!')",
                  },
                },
              ],
        },
      },
      runtime,
    ],
    displayData: {
      width: 462,
      height: 288,
      position: {
        x: 2075.7067885117494,
        y: 234.65663468515768,
      },
    },
  };

  return new NodeDataFactoryBuilder<CodeExecutionNode>(nodeData);
}

export function errorNodeDataFactory({
  errorSourceInputs,
}: {
  errorSourceInputs?: NodeInput[];
} = {}): ErrorNode {
  const errorSourceInputId = "d2287fee-98fb-421c-9464-e54d8f70f046";

  return {
    id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
    type: "ERROR",
    data: {
      label: "Error Node",
      name: "error-node",
      targetHandleId: "370d712d-3369-424e-bcf7-f4da1aef3928",
      errorSourceInputId: errorSourceInputId,
      errorOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
    },
    inputs: errorSourceInputs ?? [
      {
        id: errorSourceInputId,
        key: "error_source_input_id",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "ERROR",
                value: {
                  message: "Something went wrong!",
                  code: "USER_DEFINED_ERROR",
                },
              },
            },
          ],
          combinator: "OR",
        },
      },
    ],
  };
}

export function nodePortFactory(port: Partial<NodePort> = {}): NodePort {
  const portType = port.type ?? "DEFAULT";
  const portId = port.id ?? uuidv4();
  const portName =
    port.type === "DEFAULT"
      ? "default"
      : port.name ?? `${portType.toLowerCase()}_port`;

  if (port.type === "IF" || port.type === "ELIF") {
    return {
      type: portType,
      id: portId,
      name: portName,
      expression: port.expression ?? {
        type: "UNARY_EXPRESSION",
        operator: "null",
        lhs: {
          type: "WORKFLOW_INPUT",
          inputVariableId: "input-1",
        },
      },
    };
  }

  return {
    type: portType,
    id: portId,
    name: portName,
  };
}

export function nodePortsFactory(ports?: Partial<NodePort>[]): NodePort[] {
  return (
    ports?.map((port) => nodePortFactory(port)) ?? [
      nodePortFactory({ type: "IF" }),
      nodePortFactory({ type: "ELSE" }),
    ]
  );
}

export function genericNodeFactory({
  id,
  label: _label,
  nodeTrigger,
  nodePorts,
  nodeAttributes,
  nodeOutputs,
  adornments,
  base,
}: {
  id?: string;
  label?: string;
  nodeTrigger?: NodeTrigger;
  nodePorts?: NodePort[];
  nodeAttributes?: NodeAttribute[];
  nodeOutputs?: NodeOutput[];
  adornments?: AdornmentNode[];
  base?: CodeResourceDefinition;
} = {}): GenericNode {
  const label = _label ?? "MyCustomNode";
  const nodeData: GenericNode = {
    id: id ?? uuidv4(),
    label,
    type: WorkflowNodeType.GENERIC,
    base: base ?? {
      module: ["vellum", "workflows", "nodes", "bases", "base"],
      name: "BaseNode",
    },
    definition: {
      name: label,
      module: ["my_nodes", "my_custom_node"],
    },
    trigger: nodeTrigger ?? {
      id: "trigger-1",
      mergeBehavior: "AWAIT_ALL",
    },
    ports: nodePorts ?? [nodePortFactory()],
    attributes: nodeAttributes ?? [
      {
        id: "990d55db-9d72-452a-b074-9bee1f89ecb9",
        name: "default-attribute",
        value: {
          type: "CONSTANT_VALUE",
          value: {
            type: "STRING",
            value: "default-value",
          },
        },
      },
      {
        id: "70652383-d93f-4c3a-b194-1ea5cdced8f1",
        name: "default-attribute-2",
        value: {
          type: "WORKFLOW_INPUT",
          inputVariableId: "input-1",
        },
      },
    ],
    outputs: nodeOutputs ?? [
      {
        id: "output-1",
        name: "output",
        type: "STRING",
        value: {
          type: "CONSTANT_VALUE",
          value: {
            type: "STRING",
            value: "default-value",
          },
        },
      },
    ],
    adornments: adornments,
  };
  return nodeData;
}

export function finalOutputNodeFactory({
  includeInput = true,
  id,
  targetHandleId,
  outputId,
  name,
  label,
}: {
  includeInput?: boolean;
  id?: string;
  targetHandleId?: string;
  outputId?: string;
  name?: string;
  label?: string;
} = {}): NodeDataFactoryBuilder<FinalOutputNode> {
  const inputs: NodeInput[] = [];
  const outputs: NodeOutput[] = [];

  if (includeInput) {
    inputs.push({
      id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
      key: "node_input",
      value: {
        rules: [
          {
            type: "CONSTANT_VALUE",
            data: {
              type: "STRING",
              value: "<my-output>",
            },
          },
        ],
        combinator: "OR",
      },
    });
    outputs.push({
      id: "c013440d-930d-4953-b386-1ddd7750e831",
      name: "node_input",
      type: "STRING",
      value: {
        type: "CONSTANT_VALUE",
        value: {
          type: "STRING",
          value: "<my-output>",
        },
      },
    });
  }

  const nodeData: FinalOutputNode = {
    id: id ?? "48e0d88b-a544-4a14-b49f-38aca82e0e13",
    type: "TERMINAL",
    data: {
      label: label ?? "Final Output Node",
      outputType: "STRING",
      name: name ?? "final-output",
      targetHandleId: targetHandleId ?? "<target-handle-id>",
      nodeInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
      outputId: outputId ?? "<output-id>",
    },
    inputs: inputs,
    displayData: {
      width: 462,
      height: 288,
      position: {
        x: 2075.7067885117494,
        y: 234.65663468515768,
      },
    },
    outputs: outputs,
  };
  return new NodeDataFactoryBuilder<FinalOutputNode>(nodeData);
}

export function mapNodeDataFactory({
  outputVariables,
}: {
  outputVariables?: VellumVariable[];
} = {}): NodeDataFactoryBuilder<MapNode> {
  const entrypoint = entrypointNodeDataFactory();
  const templatingNode = templatingNodeFactory().build();
  const nodeData: MapNode = {
    id: "14fee4a0-ad25-402f-b942-104d3a5a0824",
    type: "MAP",
    data: {
      variant: "INLINE",
      label: "Map Node",
      workflowRawData: {
        nodes: [entrypoint, templatingNode],
        edges: edgesFactory([[entrypoint, templatingNode]]),
      },
      inputVariables: [
        {
          id: "83e669a8-e1c0-480c-b1d6-9467dd0021b1",
          key: "items",
          type: "JSON",
        },
        {
          id: "8e8f462c-8f07-4f5f-80dd-a33eb2cd6061",
          key: "item",
          type: "JSON",
        },
        {
          id: "95236886-08a8-4b38-8595-f330cb515698",
          key: "index",
          type: "NUMBER",
        },
      ],
      outputVariables: outputVariables ?? [
        {
          id: "edd5cfd5-6ad8-437d-8775-4b9aeb62a5fb",
          key: "final-output",
          type: "STRING",
        },
      ],
      concurrency: 4,
      sourceHandleId: "4878f525-d4a3-4e3d-9221-e146f282a96a",
      targetHandleId: "3fe4b4a6-5ed2-4307-ac1c-02389337c4f2",
      itemsInputId: "83e669a8-e1c0-480c-b1d6-9467dd0021b1",
      itemInputId: "8e8f462c-8f07-4f5f-80dd-a33eb2cd6061",
      indexInputId: "95236886-08a8-4b38-8595-f330cb515698",
    },
    inputs: [
      {
        id: "f34872c2-5c0e-45a3-b204-3af22d1028d3",
        key: "items",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "JSON",
                value: ["apple", "banana", "cherry"],
              },
            },
          ],
          combinator: "OR",
        },
      },
    ],
  };
  return new NodeDataFactoryBuilder<MapNode>(nodeData);
}

export function inlineSubworkflowNodeDataFactory({
  label,
  nodes,
}: {
  label?: string;
  nodes?: Array<WorkflowDataNode>;
} = {}): NodeDataFactoryBuilder<SubworkflowNode> {
  const entrypoint = entrypointNodeDataFactory();
  const templatingNode = templatingNodeFactory().build();
  const outputVariableId = "edd5cfd5-6ad8-437d-8775-4b9aeb62a5fb";

  const workflowNodes = [entrypoint, ...(nodes ?? [templatingNode])];

  const nodeData: SubworkflowNode = {
    id: "14fee4a0-ad25-402f-b942-104d3a5a0824",
    type: "SUBWORKFLOW",
    data: {
      variant: "INLINE",
      label: label ?? "Inline Subworkflow Node",
      workflowRawData: {
        nodes: workflowNodes,
        edges: edgesFactory([[entrypoint, templatingNode]]),
        outputValues: [
          {
            outputVariableId,
            value: {
              type: "NODE_OUTPUT",
              nodeId: templatingNode.id,
              nodeOutputId: templatingNode.data.outputId,
            },
          },
        ],
      },
      inputVariables: [],
      outputVariables: [
        {
          id: outputVariableId,
          key: "final-output",
          type: "STRING",
        },
      ],
      sourceHandleId: "4878f525-d4a3-4e3d-9221-e146f282a96a",
      targetHandleId: "3fe4b4a6-5ed2-4307-ac1c-02389337c4f2",
    },
    inputs: [],
  };
  return new NodeDataFactoryBuilder<SubworkflowNode>(nodeData);
}

export function toolCallingNodeFactory({
  id,
  label: _label,
  nodeTrigger,
  nodePorts,
  nodeAttributes,
  nodeOutputs,
  adornments,
}: {
  id?: string;
  label?: string;
  nodeTrigger?: NodeTrigger;
  nodePorts?: NodePort[];
  nodeAttributes?: NodeAttribute[];
  nodeOutputs?: NodeOutput[];
  adornments?: AdornmentNode[];
} = {}): GenericNode {
  const label = _label ?? "Tool Calling Node";
  const nodeData: GenericNode = {
    id: id ?? "a72bbfd6-9eb5-48af-9c43-55f1d0a75106",
    label,
    type: WorkflowNodeType.GENERIC,
    base: {
      name: "ToolCallingNode",
      module: [
        "vellum",
        "workflows",
        "nodes",
        "displayable",
        "tool_calling_node",
      ],
    },
    definition: undefined,
    trigger: nodeTrigger ?? {
      id: "trigger-id",
      mergeBehavior: "AWAIT_ATTRIBUTES",
    },
    ports: nodePorts ?? [
      {
        id: "7b97f998-4be5-478d-94c4-9423db5f6392",
        name: "default",
        type: "DEFAULT",
      },
    ],
    attributes: nodeAttributes ?? [
      {
        id: "75bd1347-dca2-4cba-b0b0-a20a2923ebcc",
        name: "ml_model",
        value: {
          type: "CONSTANT_VALUE",
          value: { type: "STRING", value: "gpt-4o-mini" },
        },
      },
      {
        id: "beec5344-2eff-47d2-b920-b90367370d79",
        name: "blocks",
        value: {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [
              {
                state: null,
                blocks: [
                  {
                    state: null,
                    blocks: [
                      {
                        text: "You are a weather expert",
                        state: null,
                        block_type: "PLAIN_TEXT",
                        cache_config: null,
                      },
                    ],
                    block_type: "RICH_TEXT",
                    cache_config: null,
                  },
                ],
                chat_role: "SYSTEM",
                block_type: "CHAT_MESSAGE",
                chat_source: null,
                cache_config: null,
                chat_message_unterminated: null,
              },
              {
                state: null,
                blocks: [
                  {
                    state: null,
                    blocks: [
                      {
                        state: null,
                        block_type: "VARIABLE",
                        cache_config: null,
                        input_variable: "question",
                      },
                    ],
                    block_type: "RICH_TEXT",
                    cache_config: null,
                  },
                ],
                chat_role: "USER",
                block_type: "CHAT_MESSAGE",
                chat_source: null,
                cache_config: null,
                chat_message_unterminated: null,
              },
            ],
          },
        },
      },
      {
        id: "7b1ab802-3228-43b3-a493-734c94794710",
        name: "functions",
        value: {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [
              {
                type: "CODE_EXECUTION",
                src: 'def get_current_weather(location: str, unit: str) -> str:\n    """\n    Get the current weather in a given location.\n    """\n    return f"The current weather in {location} is sunny with a temperature of 70 degrees {unit}."\n',
                name: "get_current_weather",
                description: "Get the current weather in a given location.",
                definition: {
                  name: "get_current_weather",
                  state: null,
                  forced: null,
                  strict: null,
                  parameters: {
                    type: "object",
                    required: ["location", "unit"],
                    properties: {
                      unit: { type: "string" },
                      location: { type: "string" },
                    },
                  },
                  description: null,
                  cache_config: null,
                },
              },
            ],
          },
        },
      },
      {
        id: "38cf126e-a186-4a63-8e30-47c4507413cd",
        name: "prompt_inputs",
        value: {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: { question: "What's the weather like in San Francisco?" },
          },
        },
      },
      {
        id: "a7f8a575-a7ce-40b9-8bc9-546303f511c1",
        name: "parameters",
        value: {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: {
              stop: [],
              top_k: 0,
              top_p: 1,
              logit_bias: {},
              max_tokens: 1000,
              temperature: 0,
              presence_penalty: 0,
              custom_parameters: { tool_choice: "AUTO" },
              frequency_penalty: 0,
            },
          },
        },
      },
      {
        id: "723f614a-be30-4f27-90d0-896c740e58d3",
        name: "max_tool_calls",
        value: {
          type: "CONSTANT_VALUE",
          value: { type: "NUMBER", value: 1.0 },
        },
      },
    ],
    outputs: nodeOutputs ?? [],
    adornments: adornments,
  };
  return nodeData;
}
