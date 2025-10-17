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
        id: "first-generic-node",
        type: "GENERIC",
        label: "First Generic Node",
        data: {
          source_handle_id: "first-generic-source",
          target_handle_id: "first-generic-target",
        },
        inputs: [],
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
        base: {
          name: "SharedBaseNode",
          module: ["testing", "nodes", "shared_base_node"],
        },
        definition: {
          name: "FirstGenericNode",
          module: ["testing", "nodes", "first_generic_node"],
        },
        trigger: {
          id: "first-generic-target",
          merge_behavior: "AWAIT_ANY",
        },
        ports: [
          {
            id: "first-generic-source",
            name: "default",
            type: "DEFAULT",
          },
        ],
        adornments: null,
        outputs: [
          {
            id: "first-output-id",
            name: "value",
            type: "STRING",
            value: undefined,
          },
        ],
        attributes: [],
      },
      {
        id: "second-generic-node",
        type: "GENERIC",
        label: "Second Generic Node",
        data: {
          source_handle_id: "second-generic-source",
          target_handle_id: "second-generic-target",
        },
        inputs: [],
        display_data: {
          position: {
            x: 500,
            y: 400,
          },
          z_index: 1,
          comment: null,
          width: 330.0,
          height: 96.0,
          icon: null,
          color: null,
        },
        base: {
          name: "SharedBaseNode",
          module: ["testing", "nodes", "shared_base_node"],
        },
        definition: {
          name: "FirstGenericNode",
          module: ["testing", "nodes", "first_generic_node"],
        },
        trigger: {
          id: "second-generic-target",
          merge_behavior: "AWAIT_ANY",
        },
        ports: [
          {
            id: "second-generic-source",
            name: "default",
            type: "DEFAULT",
          },
        ],
        adornments: null,
        outputs: [
          {
            id: "second-output-id",
            name: "value",
            type: "STRING",
            value: undefined,
          },
        ],
        attributes: [],
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
                  type: "BINARY_EXPRESSION",
                  data: {
                    type: "BINARY_EXPRESSION",
                    operator: "coalesce",
                    lhs: {
                      type: "NODE_OUTPUT",
                      node_id: "first-generic-node",
                      output_id: "first-output-id",
                    },
                    rhs: {
                      type: "NODE_OUTPUT",
                      node_id: "second-generic-node",
                      output_id: "second-output-id",
                    },
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
            y: 300,
          },
          z_index: 2,
          comment: null,
          width: 330.0,
          height: 96.0,
          icon: null,
          color: null,
        },
        base: null,
        definition: {
          name: "FinalOutputNode",
          module: ["testing", "nodes", "final_output_node"],
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
              type: "BINARY_EXPRESSION",
              operator: "coalesce",
              lhs: {
                type: "NODE_OUTPUT",
                node_id: "first-generic-node",
                node_output_id: "first-output-id",
              },
              rhs: {
                type: "NODE_OUTPUT",
                node_id: "second-generic-node",
                node_output_id: "second-output-id",
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
        target_node_id: "first-generic-node",
        target_handle_id: "first-generic-target",
        type: "DEFAULT",
      },
      {
        id: "edge-2",
        source_node_id: "entrypoint-node",
        source_handle_id: "entrypoint-source",
        target_node_id: "second-generic-node",
        target_handle_id: "second-generic-target",
        type: "DEFAULT",
      },
      {
        id: "edge-3",
        source_node_id: "first-generic-node",
        source_handle_id: "first-generic-source",
        target_node_id: "terminal-node",
        target_handle_id: "terminal-target",
        type: "DEFAULT",
      },
      {
        id: "edge-4",
        source_node_id: "second-generic-node",
        source_handle_id: "second-generic-source",
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
  assertions: ["workflow.py", "nodes/final_output_node.py"],
};
