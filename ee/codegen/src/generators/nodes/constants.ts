export enum AttributeType {
  WorkflowErrorCode = "WorkflowErrorCode",
  PromptBlocks = "PromptBlocks",
  Functions = "Functions",
  Parameters = "Parameters",
}

export interface AttributeConfig {
  defaultValue: unknown;
  type?: AttributeType;
}

export const NODE_ATTRIBUTES: Record<
  string,
  Record<string, AttributeConfig>
> = {
  // From src/vellum/workflows/nodes/core/retry_node/node.py
  RetryNode: {
    retry_on_error_code: {
      defaultValue: null,
      type: AttributeType.WorkflowErrorCode,
    },
    retry_on_condition: {
      defaultValue: null,
    },
    delay: {
      defaultValue: null,
    },
  },
  TryNode: {
    on_error_code: {
      defaultValue: null,
      type: AttributeType.WorkflowErrorCode,
    },
  },
  ToolCallingNode: {
    blocks: {
      defaultValue: null,
      type: AttributeType.PromptBlocks,
    },
    functions: {
      defaultValue: null,
      type: AttributeType.Functions,
    },
    parameters: {
      defaultValue: null,
      type: AttributeType.Parameters,
    },
  },
};
