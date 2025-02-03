import { v4 as uuidv4 } from "uuid";
import { VellumVariableType, PromptParameters } from "vellum-ai/api";

import { VellumValueLogicalExpressionSerializer } from "src/serializers/vellum";
import {
  EntrypointNode,
  CodeExecutionNode,
  GuardrailNode,
  SearchNode,
  FinalOutputNode,
  WorkflowNodeType,
  PromptNode,
  TemplatingNode,
  ConditionalNode,
  ApiNode,
  MergeNode,
  GenericNode,
  SubworkflowNode,
  NoteNode,
  ErrorNode,
  NodeInputValuePointerRule,
  PromptTemplateBlock,
  VellumLogicalConditionGroup,
  ConditionalNodeConditionData,
  NodeOutputData,
  NodeInput,
  MapNode,
  NodeTrigger,
  NodePort,
  NodeAttribute,
  NodeOutput,
  AdornmentNode,
  ConstantValuePointer,
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

export function mergeNodeDataFactory(numTargetHandles: number = 2): MergeNode {
  return {
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
}

export function searchNodeDataFactory(args?: {
  metadataFiltersNodeInputId?: string;
  metadataFilters?: VellumLogicalConditionGroup;
  metadataFilterInputs?: NodeInput[];
  errorOutputId?: string;
  limitInput?: ConstantValuePointer;
  includeDocumentIndexInput?: boolean;
}): SearchNode {
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
      queryNodeInputId: "f3a0d8b9-7772-4db6-8e28-f49f8c4d9e2a",
      documentIndexNodeInputId: "b49bc1ab-2ad5-4cf2-8966-5cc87949900d",
      weightsNodeInputId: "1daf3180-4b92-472a-8665-a7703c84a94e",
      limitNodeInputId: "161d264e-d04e-4c37-8e50-8bbb4c90c46e",
      separatorNodeInputId: "4eddefc0-90d5-422a-aec2-bc94c8f1d83c",
      resultMergingEnabledNodeInputId: "dc9f880b-81bc-4644-b025-8f7d5db23a48",
      externalIdFiltersNodeInputId: "61933e79-b0c2-4e3c-bf07-e2d93b9d9c54",
      metadataFiltersNodeInputId:
        metadataFiltersNodeInputId ?? "7c43b315-d1f2-4727-9540-6cc3fd4641f3",
    },
    inputs: [
      {
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
      },
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

  return nodeData;
}

export function noteNodeDataFactory(): NoteNode {
  return {
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
}

export function guardrailNodeDataFactory({
  errorOutputId,
}: {
  errorOutputId?: string;
} = {}): GuardrailNode {
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
    inputs: [
      {
        id: "3f917af8-03a4-4ca4-8d40-fa662417fe9c",
        key: "expected",
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
      },
      {
        id: "bed55ada-923e-46ef-8340-1a5b0b563dc1",
        key: "actual",
        value: {
          rules: [
            {
              type: "INPUT_VARIABLE",
              data: {
                inputVariableId: "1472503c-1662-4da9-beb9-73026be90c68",
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
}: {
  blockType?: string;
  errorOutputId?: string;
  parameters?: PromptParameters;
  defaultBlock?: PromptTemplateBlock;
}): PromptNode {
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
      },
      mlModelName: "gpt-4o-mini",
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
  fallbackModels,
}: {
  errorOutputId?: string;
  fallbackModels?: string[];
} = {}): PromptNode {
  return {
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
      fallbackModels,
    },
    inputs: [
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
}

export function templatingNodeFactory({
  id,
  label,
  sourceHandleId,
  targetHandleId,
  errorOutputId,
  outputType = VellumVariableType.String,
  inputs,
  template,
}: {
  id?: string;
  label?: string;
  sourceHandleId?: string;
  targetHandleId?: string;
  errorOutputId?: string;
  outputType?: VellumVariableType;
  inputs?: NodeInput[];
  template?: ConstantValuePointer;
} = {}): TemplatingNode {
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
      outputId: "2d4f1826-de75-499a-8f84-0a690c8136ad",
      errorOutputId,
      sourceHandleId: sourceHandleId ?? "6ee2c814-d0a5-4ec9-83b6-45156e2f22c4",
      targetHandleId: targetHandleId ?? "3960c8e1-9baa-4b9c-991d-e399d16a45aa",
      templateNodeInputId: "7b8af68b-cf60-4fca-9c57-868042b5b616",
      outputType: outputType,
    },
    inputs: nodeInputs,
  };
  return nodeData;
}

export function subworkflowDeploymentNodeDataFactory(): SubworkflowNode {
  return {
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
  includeElif = false,
}: {
  id?: string;
  label?: string;
  targetHandleId?: string;
  ifSourceHandleId?: string;
  elseSourceHandleId?: string;
  inputReferenceId?: string;
  inputReferenceNodeId?: string;
  includeElif?: boolean;
} = {}): ConditionalNode {
  const conditions: ConditionalNodeConditionData[] = [];
  conditions.push({
    id: "8d0d8b56-6c17-4684-9f16-45dd6ce23060",
    type: "IF",
    sourceHandleId: ifSourceHandleId ?? "63345ab5-1a4d-48a1-ad33-91bec41f92a5",
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
  });
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
    inputs:
      inputReferenceId && inputReferenceNodeId
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
  return nodeData;
}

export type ApiNodeFactoryProps = {
  errorOutputId?: string;
  bearerToken?: NodeInput;
  apiKeyHeaderValue?: NodeInput;
  additionalHeaders?: {
    key: NodeInput;
    value: NodeInput;
  }[];
};

export function apiNodeFactory({
  errorOutputId,
  bearerToken,
  apiKeyHeaderValue,
  additionalHeaders,
}: ApiNodeFactoryProps = {}): ApiNode {
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
                type: "INPUT_VARIABLE",
                data: {
                  inputVariableId: "5f64210f-ec43-48ce-ae40-40a9ba4c4c11",
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
                type: "INPUT_VARIABLE",
                data: {
                  inputVariableId: "b81c5c88-9528-47d0-8106-14a75520ed47",
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
                type: "INPUT_VARIABLE",
                data: {
                  inputVariableId: "b81c5c88-9528-47d0-8106-14a75520ed47",
                },
              },
            ],
            combinator: "OR",
          },
        },
      },
    ] as { key: NodeInput; value: NodeInput }[]);

  const nodeData: ApiNode = {
    id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
    type: "API",
    data: {
      label: "API Node",
      methodInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
      urlInputId: "480a4c12-22d6-4223-a38a-85db5eda118c",
      bodyInputId: "74865eb7-cdaf-4d40-a499-0a6505e72680",
      authorizationTypeInputId: "de330dac-05b1-4e78-bee7-7452203af3d5",
      bearerTokenValueInputId: bearerTokenInput.id,
      apiKeyHeaderKeyInputId: "96c8343d-cc94-4df0-9001-eb2905a00be7",
      apiKeyHeaderValueInputId: apiKeyHeaderValueInput.id,
      additionalHeaders: additionalHeaderInputs.map(({ key, value }) => ({
        headerKeyInputId: key.id,
        headerValueInputId: value.id,
      })),
      textOutputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
      jsonOutputId: "af576eaa-d39d-4c19-8992-1f01a65a709a",
      statusCodeOutputId: "69250713-617d-42a4-9326-456c70d0ef20",
      errorOutputId,
      targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
      sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
    },
    inputs: [
      {
        id: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
        key: "method",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "POST",
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: "480a4c12-22d6-4223-a38a-85db5eda118c",
        key: "url",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "fasdfadsf",
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: "74865eb7-cdaf-4d40-a499-0a6505e72680",
        key: "body",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "JSON",
                value: {},
              },
            },
          ],
          combinator: "OR",
        },
      },
      {
        id: "de330dac-05b1-4e78-bee7-7452203af3d5",
        key: "authorization_type",
        value: {
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "API_KEY",
              },
            },
          ],
          combinator: "OR",
        },
      },
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
  return nodeData;
}

export function codeExecutionNodeFactory({
  codeInputValueRule,
  runtime,
}: {
  codeInputValueRule?: NodeInputValuePointerRule;
  runtime?: string;
} = {}): CodeExecutionNode {
  const nodeData: CodeExecutionNode = {
    id: "2cd960a3-cb8a-43ed-9e3f-f003fc480951",
    type: "CODE_EXECUTION",
    data: {
      label: "Code Execution Node",
      codeInputId: "9bf086d4-feed-47ff-9736-a5a6aa3a11cc",
      outputId: "81b270c0-4deb-4db3-aae5-138f79531b2b",
      outputType: "STRING",
      runtimeInputId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
      targetHandleId: "06573a05-e6f0-48b9-bc6e-07e06d0bc1b1",
      sourceHandleId: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
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
                    value: "print('Hello, World!')",
                  },
                },
              ],
        },
      },
      {
        id: "c38a71f6-3ffb-45fa-9eea-93c6984a9e3e",
        key: "runtime",
        value: {
          combinator: "OR",
          rules: [
            {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: runtime ? runtime : "PYTHON_3_11",
              },
            },
          ],
        },
      },
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
  return nodeData;
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
  const portName = port.name ?? `${portType.toLowerCase()}_port`;

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

export function genericNodeFactory(
  {
    id,
    name,
    nodeTrigger,
    nodePorts,
    nodeAttributes,
    nodeOutputs,
    adornments,
  }: {
    id?: string;
    name: string;
    nodeTrigger?: NodeTrigger;
    nodePorts?: NodePort[];
    nodeAttributes?: NodeAttribute[];
    nodeOutputs?: NodeOutput[];
    adornments?: AdornmentNode[];
  } = {
    name: "MyCustomNode",
  }
): GenericNode {
  const nodeData: GenericNode = {
    id: id ?? uuidv4(),
    type: WorkflowNodeType.GENERIC,
    base: {
      module: ["vellum", "workflows", "nodes", "bases", "base"],
      name: "BaseNode",
    },
    definition: {
      name,
      module: ["my_nodes", "my_custom_node"],
    },
    trigger: nodeTrigger ?? {
      id: "trigger-1",
      mergeBehavior: "AWAIT_ALL",
    },
    ports: nodePorts ?? [nodePortFactory()],
    attributes: nodeAttributes ?? [
      {
        id: "attr-1",
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
        id: "attr-2",
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
} = {}): FinalOutputNode {
  const inputs: NodeInput[] = [];

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
  };
  return nodeData;
}

export function mapNodeDataFactory(): MapNode {
  return {
    id: "14fee4a0-ad25-402f-b942-104d3a5a0824",
    type: "MAP",
    data: {
      variant: "INLINE",
      label: "Map Node",
      workflowRawData: {
        nodes: [
          {
            id: "817b520f-a6f6-40c9-8e98-68a4586360d6",
            type: "TEMPLATING",
            data: {
              label: "Templating Node with Reference",
              outputId: "db5bcad3-d9f9-4314-a198-8748f4a824a2",
              sourceHandleId: "7ac839c3-e443-4eee-8897-aeb4c82531c2",
              targetHandleId: "d85e6190-3353-4e1e-9098-97f828eef712",
              templateNodeInputId: "3211e289-efce-451f-a12a-311f05f3dbf0",
              outputType: "STRING",
            },
            inputs: [
              {
                id: "4271329e-f375-4245-9b62-3d300b9b5cfa",
                key: "example_var_1",
                value: {
                  rules: [],
                  combinator: "OR",
                },
              },
              {
                id: "1a11b7c8-7b04-43bf-a9b3-a9669464b6d0",
                key: "template",
                value: {
                  rules: [
                    {
                      type: "CONSTANT_VALUE",
                      data: {
                        type: "STRING",
                        value: "{{ example_var_1 }}",
                      },
                    },
                  ],
                  combinator: "OR",
                },
              },
            ],
            displayData: {
              position: {
                x: 405.85703120354856,
                y: 140.63171864439244,
              },
              width: 480.0,
              height: 224.0,
            },
          },
        ],
        edges: [],
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
      outputVariables: [
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
              type: "INPUT_VARIABLE",
              data: {
                inputVariableId: "ce97c6fd-4a41-40c4-bd4b-9b264c58d2d1",
              },
            },
          ],
          combinator: "OR",
        },
      },
    ],
  };
}
