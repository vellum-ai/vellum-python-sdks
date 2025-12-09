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
        id: "start-node",
        type: "GENERIC",
        label: "Start Node",
        base: {
          name: "BaseNode",
          module: ["vellum", "workflows", "nodes", "bases", "base"],
        },
        definition: {
          name: "StartNode",
          module: ["testing", "nodes", "start_node"],
        },
        trigger: {
          id: "start-target",
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        outputs: [
          {
            id: "node-output-id",
            name: "result",
            type: "STRING",
            value: null,
          },
        ],
        ports: [],
        attributes: [],
      },
    ],
    edges: [
      {
        id: "edge-1",
        source_node_id: "entrypoint-node",
        source_handle_id: "entrypoint-source",
        target_node_id: "start-node",
        target_handle_id: "start-target",
        type: "DEFAULT",
      },
    ],
    output_values: [
      {
        output_variable_id: "workflow-output-variable-id",
        value: {
          type: "NODE_OUTPUT",
          node_id: "start-node",
          node_output_id: "node-output-id",
        },
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
  dataset: [
    {
      id: "first-scenario",
      label: "First Scenario",
      inputs: [],
      mocks: [
        {
          node_id: "start-node",
          when_condition: {
            type: "BINARY_EXPRESSION",
            operator: ">=",
            lhs: {
              type: "EXECUTION_COUNTER",
              node_id: "start-node",
            },
            rhs: {
              type: "CONSTANT_VALUE",
              value: {
                type: "STRING",
                value: "Hello, World!",
              },
            },
          },
          then_outputs: {
            result: "Hello, World!",
          },
        },
      ],
    },
  ],
  assertions: ["sandbox.py"],
};
