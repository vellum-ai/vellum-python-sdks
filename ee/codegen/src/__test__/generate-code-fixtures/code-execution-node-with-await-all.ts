export default {
  workflow_raw_data: {
    nodes: [
      {
        id: "entrypoint-node",
        type: "ENTRYPOINT",
        data: {
          label: "Entrypoint",
          source_handle_id: "entrypoint-source",
        },
        inputs: [],
      },
      {
        id: "code-execution-node",
        type: "CODE_EXECUTION",
        data: {
          label: "Code Execution Node",
          output_id: "code-output-id",
          error_output_id: null,
          log_output_id: "log-output-id",
          source_handle_id: "code-source",
          target_handle_id: "code-target",
          code_input_id: "code-input-id",
          runtime_input_id: "runtime-input-id",
          output_type: "STRING",
          packages: null,
        },
        inputs: [
          {
            id: "code-input-id",
            key: "code",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value:
                      "def main() -> str:\n    return 'Hello from AWAIT_ALL'\n",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "runtime-input-id",
            key: "runtime",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "PYTHON_3_11_6",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
        display_data: {
          position: {
            x: 500,
            y: 200,
          },
          z_index: 1,
          comment: null,
          width: 480.0,
          height: 224.0,
          icon: null,
          color: null,
        },
        base: null,
        definition: {
          name: "CodeExecutionWithAwaitAll",
          module: ["testing", "nodes", "code_execution_with_await_all"],
        },
        trigger: {
          id: "code-target",
          merge_behavior: "AWAIT_ALL",
        },
        ports: [
          {
            id: "code-source",
            name: "default",
            type: "DEFAULT",
          },
        ],
        adornments: null,
        outputs: null,
        attributes: null,
      },
      {
        id: "terminal-node",
        type: "TERMINAL",
        data: {
          label: "Final Output",
          name: "result",
          target_handle_id: "terminal-target",
          output_id: "terminal-output-id",
          output_type: "STRING",
          node_input_id: "terminal-node-input-id",
        },
        inputs: [
          {
            id: "terminal-node-input-id",
            key: "node_input",
            value: {
              rules: [
                {
                  type: "NODE_OUTPUT",
                  data: {
                    node_id: "code-execution-node",
                    output_id: "code-output-id",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
        display_data: {
          position: {
            x: 1000,
            y: 200,
          },
          z_index: 2,
          comment: null,
          width: 480.0,
          height: 234.0,
          icon: null,
          color: null,
        },
        base: null,
        definition: {
          name: "UseCodeExecutionWithAwaitAll",
          module: ["testing", "nodes", "use_code_execution_with_await_all"],
        },
        trigger: {
          id: "terminal-target",
          merge_behavior: "AWAIT_ANY",
        },
        outputs: [
          {
            id: "terminal-output-id",
            name: "value",
            type: "STRING",
            value: {
              type: "NODE_OUTPUT",
              node_id: "code-execution-node",
              node_output_id: "code-output-id",
            },
          },
        ],
      },
    ],
    edges: [
      {
        id: "edge-1",
        source_node_id: "entrypoint-node",
        source_handle_id: "entrypoint-source",
        target_node_id: "code-execution-node",
        target_handle_id: "code-target",
        type: "DEFAULT",
      },
      {
        id: "edge-2",
        source_node_id: "code-execution-node",
        source_handle_id: "code-source",
        target_node_id: "terminal-node",
        target_handle_id: "terminal-target",
        type: "DEFAULT",
      },
    ],
  },
  input_variables: [],
  output_variables: [
    {
      id: "terminal-output-id",
      key: "result",
      type: "STRING",
    },
  ],
  assertions: ["nodes/code_execution_with_await_all/__init__.py"],
};
