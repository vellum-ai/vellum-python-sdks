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
        id: "top-node",
        type: "GENERIC",
        label: "Top Node",
        display_data: null,
        base: {
          name: "BaseNode",
          module: ["vellum", "workflows", "nodes", "bases", "base"],
        },
        definition: {
          name: "TopNode",
          module: ["testing", "nodes", "top_node"],
        },
        trigger: {
          id: "top-target",
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        ports: [
          {
            id: "top-default-port-id",
            name: "default",
            type: "DEFAULT",
          },
        ],
        outputs: [],
        attributes: [],
      },
      {
        id: "bottom-node",
        type: "GENERIC",
        label: "Bottom Node",
        display_data: null,
        base: {
          name: "BaseNode",
          module: ["vellum", "workflows", "nodes", "bases", "base"],
        },
        definition: {
          name: "BottomNode",
          module: ["testing", "nodes", "bottom_node"],
        },
        trigger: {
          id: "bottom-target",
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        ports: [
          {
            id: "bottom-default-port-id",
            name: "default",
            type: "DEFAULT",
          },
        ],
        outputs: [],
        attributes: [],
      },
    ],
    edges: [
      {
        id: "edge-1",
        source_node_id: "entrypoint-node",
        source_handle_id: "entrypoint-source",
        target_node_id: "top-node",
        target_handle_id: "top-target",
        type: "DEFAULT",
      },
      {
        id: "edge-2",
        source_node_id: "slack-message-trigger",
        source_handle_id: "slack-message-trigger",
        target_node_id: "bottom-node",
        target_handle_id: "bottom-target",
        type: "DEFAULT",
      },
    ],
    output_values: [],
  },
  input_variables: [],
  output_variables: [],
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
          name: "message",
          value: null,
        },
        {
          id: "channel-attribute-id",
          name: "channel",
          value: null,
        },
        {
          id: "timestamp-attribute-id",
          name: "timestamp",
          value: null,
        },
      ],
      display_data: {
        label: "Slack Message Trigger",
        position: {
          x: 100,
          y: 200,
        },
        z_index: 1,
        icon: "slack",
        color: "#4A154B",
      },
    },
  ],
  assertions: ["workflow.py", "triggers/slack_message_trigger.py"],
};
