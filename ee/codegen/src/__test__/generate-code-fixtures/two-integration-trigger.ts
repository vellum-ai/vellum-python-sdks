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
                    value: "Triggered!",
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
                value: "Triggered!",
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
      {
        id: "edge-2",
        source_node_id: "linear-integration-trigger",
        source_handle_id: "linear-integration-trigger",
        target_node_id: "terminal-node",
        target_handle_id: "terminal-target",
        type: "DEFAULT",
      },
      {
        id: "edge-3",
        source_node_id: "linear-integration-trigger-2",
        source_handle_id: "linear-integration-trigger-2",
        target_node_id: "terminal-node",
        target_handle_id: "terminal-target",
        type: "DEFAULT",
      },
    ],
    output_values: [
      {
        output_variable_id: "workflow-output-variable-id",
        value: {
          type: "NODE_OUTPUT",
          node_id: "terminal-node",
          node_output_id: "terminal-node-output-id",
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
  triggers: [
    {
      id: "linear-integration-trigger",
      type: "INTEGRATION",
      exec_config: {
        type: "COMPOSIO",
        integration_name: "LINEAR",
        slug: "LINEAR_COMMENT_EVENT_TRIGGER",
        setup_attributes: [
          {
            id: "aca3336a-6733-4c67-bd9c-162c77ca400e",
            key: "team_id",
            type: "STRING",
            required: true,
            default: {
              type: "STRING",
              value: "dfasadf",
            },
            extensions: null,
          },
        ],
      },
      attributes: [
        {
          id: "action-attribute-id",
          key: "action",
          type: "STRING",
        },
        {
          id: "data-attribute-id",
          key: "data",
          type: "JSON",
        },
        {
          id: "type-attribute-id",
          key: "type",
          type: "STRING",
        },
        {
          id: "url-attribute-id",
          key: "url",
          type: "STRING",
        },
      ],
      display_data: {
        label: "Linear Integration Trigger",
        position: {
          x: 100,
          y: 200,
        },
        z_index: 1,
        icon: "linear",
        color: "#4A154B",
      },
    },
    {
      id: "linear-integration-trigger-2",
      type: "INTEGRATION",
      exec_config: {
        type: "COMPOSIO",
        integration_name: "LINEAR",
        slug: "LINEAR_COMMENT_EVENT_TRIGGER",
        setup_attributes: [
          {
            id: "aca3336a-6733-4c67-bd9c-162c77ca400e-2",
            key: "team_id",
            type: "STRING",
            required: true,
            default: {
              type: "STRING",
              value: "dfasadf",
            },
            extensions: null,
          },
        ],
      },
      attributes: [
        {
          id: "action-attribute-id-2",
          key: "action",
          type: "STRING",
        },
        {
          id: "data-attribute-id-2",
          key: "data",
          type: "JSON",
        },
        {
          id: "type-attribute-id-2",
          key: "type",
          type: "STRING",
        },
        {
          id: "url-attribute-id-2",
          key: "url",
          type: "STRING",
        },
      ],
      display_data: {
        label: "Linear Integration Trigger 2",
        position: {
          x: 300,
          y: 200,
        },
        z_index: 1,
        icon: "linear",
        color: "#4A154B",
      },
    },
  ],
  assertions: [
    "workflow.py",
    "triggers/linear_comment_event_trigger.py",
    "triggers/linear_comment_event_trigger_1.py",
  ],
};
