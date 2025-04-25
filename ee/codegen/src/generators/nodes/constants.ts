interface AdornmentAttributeConfig {
  defaultValue: unknown;
  type?: "WorkflowErrorCode" | string;
}

export const NODE_DEFAULT_ATTRIBUTES: Record<
  string,
  Record<string, AdornmentAttributeConfig>
> = {
  // From src/vellum/workflows/nodes/core/retry_node/node.py
  RetryNode: {
    retry_on_error_code: { defaultValue: null, type: "WorkflowErrorCode" },
    retry_on_condition: { defaultValue: null },
    delay: { defaultValue: null },
  },
  TryNode: {
    on_error_code: { defaultValue: null, type: "WorkflowErrorCode" },
  },
};
