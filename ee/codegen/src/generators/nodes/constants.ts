export enum AttributeType {
  WorkflowErrorCode = "WorkflowErrorCode",
  PromptBlocks = "PromptBlocks",
  Functions = "Functions",
}

export interface AttributeConfig {
  defaultValue: unknown;
  type?: AttributeType;
  name: string;
}

export const NODE_ATTRIBUTES: Record<
  string,
  Record<string, AttributeConfig>
> = {
  // From src/vellum/workflows/nodes/core/retry_node/node.py
  RetryNode: {
    retry_on_error_code: {
      name: "retry_on_error_code",
      defaultValue: null,
      type: AttributeType.WorkflowErrorCode,
    },
    retry_on_condition: { name: "retry_on_condition", defaultValue: null },
    delay: { name: "delay", defaultValue: null },
  },
  TryNode: {
    on_error_code: {
      name: "on_error_code",
      defaultValue: null,
      type: AttributeType.WorkflowErrorCode,
    },
  },
  ToolCallingNode: {
    blocks: {
      name: "blocks",
      defaultValue: null,
      type: AttributeType.PromptBlocks,
    },
    functions: {
      name: "functions",
      defaultValue: null,
      type: AttributeType.Functions,
    },
  },
};
