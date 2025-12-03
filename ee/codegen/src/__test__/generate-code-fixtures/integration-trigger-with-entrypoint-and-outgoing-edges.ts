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
        id: "custom-node",
        type: "GENERIC",
        label: "Custom Node",
        display_data: {
          position: {
            x: 100,
            y: 100,
          },
        },
        base: {
          name: "BaseNode",
          module: ["vellum", "workflows", "nodes", "bases", "base"],
        },
        definition: {
          name: "CustomNode",
          module: ["testing", "nodes", "custom_node"],
        },
        trigger: {
          id: "custom-target",
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        ports: [
          {
            id: "custom-default-port-id",
            name: "default",
            type: "DEFAULT",
          },
        ],
        outputs: [],
        attributes: [],
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
        target_node_id: "custom-node",
        target_handle_id: "custom-target",
        type: "DEFAULT",
      },
      {
        id: "integration-trigger-edge",
        source_node_id: "slack-message-trigger",
        source_handle_id: "slack-message-trigger",
        target_node_id: "custom-node",
        target_handle_id: "custom-target",
        type: "DEFAULT",
      },
      {
        id: "custom-to-output-edge",
        source_node_id: "custom-node",
        source_handle_id: "custom-default-port-id",
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
      id: "slack-message-trigger",
      type: "INTEGRATION",
      exec_config: {
        type: "COMPOSIO",
        integration_name: "slack",
        slug: "SLACK_MESSAGE_TRIGGER",
        setup_attributes: [],
      },
      attributes: [
        {
          id: "message-attribute-id",
          key: "message",
          type: "STRING",
        },
      ],
      display_data: {
        label: "Slack Message Trigger",
        position: {
          x: 0,
          y: 0,
        },
        z_index: 0,
        icon: "slack",
        color: "#4A154B",
        comment: null,
      },
    },
  ],
  assertions: ["workflow.py", "triggers/slack_message_trigger.py"],
};
