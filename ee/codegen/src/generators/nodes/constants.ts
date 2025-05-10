export interface AttributeConfig {
  defaultValue: unknown;
  type?: "WorkflowErrorCode" | string;
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
      type: "WorkflowErrorCode",
    },
    retry_on_condition: { name: "retry_on_condition", defaultValue: null },
    delay: { name: "delay", defaultValue: null },
  },
  TryNode: {
    on_error_code: {
      name: "on_error_code",
      defaultValue: null,
      type: "WorkflowErrorCode",
    },
  },
  ToolCallingNode: {
    blocks: {
      name: "blocks",
      defaultValue: null,
      type: "blocks",
    },
    functions: {
      name: "functions",
      defaultValue: null,
      type: "functions",
    },
  },
};
