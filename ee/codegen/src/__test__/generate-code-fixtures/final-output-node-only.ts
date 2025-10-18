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
        id: "terminal-node",
        type: "TERMINAL",
        data: {
          label: "Final Output",
          name: "result",
          target_handle_id: "terminal-target",
          output_id: "terminal-node-output-id",
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
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "Hello, World!",
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
          width: 330.0,
          height: 96.0,
          icon: null,
          color: null,
        },
        base: null,
        definition: {
          name: "MyFinalOutput",
          module: ["testing", "nodes", "my_final_output"],
        },
        trigger: {
          id: "terminal-target",
          merge_behavior: "AWAIT_ANY",
        },
        outputs: [
          {
            id: "node-output-id",
            name: "value",
            type: "STRING",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "STRING",
                value: "Hello, World!",
              },
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
        target_node_id: "terminal-node",
        target_handle_id: "terminal-target",
        type: "DEFAULT",
      },
    ],
  },
  input_variables: [],
  output_variables: [
    {
      id: "workflow-output-variable-id",
      key: "result",
      type: "STRING",
    },
  ],
  assertions: ["display/workflow.py", "display/nodes/my_final_output.py"],
};
