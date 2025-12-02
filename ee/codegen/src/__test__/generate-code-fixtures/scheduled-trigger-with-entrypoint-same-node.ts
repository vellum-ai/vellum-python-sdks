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
        id: "final-output-node",
        type: "TERMINAL",
        data: {
          label: "Final Output",
          name: "result",
          target_handle_id: "final-output-target",
          output_id: "final-output-id",
          output_type: "STRING",
          node_input_id: "final-output-input-id",
        },
        inputs: [
          {
            id: "final-output-input-id",
            key: "node_input",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "hello",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
        display_data: {
          position: {
            x: 300,
            y: 100,
          },
        },
      },
    ],
    edges: [
      {
        id: "entrypoint-edge",
        source_node_id: "entrypoint-node",
        source_handle_id: "entrypoint-source",
        target_node_id: "final-output-node",
        target_handle_id: "final-output-target",
        type: "DEFAULT",
      },
      {
        id: "scheduled-trigger-edge",
        source_node_id: "scheduled-trigger-id",
        source_handle_id: "scheduled-trigger-id",
        target_node_id: "final-output-node",
        target_handle_id: "final-output-target",
        type: "DEFAULT",
      },
    ],
    output_values: [],
  },
  input_variables: [],
  output_variables: [
    {
      id: "final-output-id",
      key: "result",
      type: "STRING",
    },
  ],
  triggers: [
    {
      id: "scheduled-trigger-id",
      type: "SCHEDULED",
      cron: "0 9 * * *",
      timezone: "UTC",
      attributes: [],
      definition: null,
      display_data: {
        label: "Daily Schedule",
        position: {
          x: 0,
          y: 0,
        },
        z_index: 0,
        icon: null,
        color: null,
        comment: null,
      },
    },
  ],
  assertions: ["workflow.py", "triggers/daily_schedule.py"],
};
