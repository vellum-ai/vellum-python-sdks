interface AttributeConfig {
  defaultValue: unknown;
}

export const NODE_DEFAULT_ATTRIBUTES: Record<
  string,
  Record<string, AttributeConfig>
> = {
  // From src/vellum/workflows/nodes/core/retry_node/node.py
  RetryNode: {
    retry_on_error_code: { defaultValue: undefined },
    retry_on_condition: { defaultValue: undefined },
    delay: { defaultValue: undefined },
  },
};
