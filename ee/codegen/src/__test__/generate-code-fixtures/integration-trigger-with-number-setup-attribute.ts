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
        source_node_id: "gmail-integration-trigger",
        source_handle_id: "gmail-integration-trigger",
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
      id: "gmail-integration-trigger",
      type: "INTEGRATION",
      exec_config: {
        type: "COMPOSIO",
        integration_name: "GMAIL",
        slug: "GMAIL_NEW_GMAIL_MESSAGE",
        setup_attributes: [
          {
            id: "interval-attribute-id",
            key: "interval",
            type: "NUMBER",
            required: true,
            default: {
              type: "NUMBER",
              value: 1,
            },
            extensions: null,
          },
          {
            id: "user-id-attribute-id",
            key: "user_id",
            type: "STRING",
            required: true,
            default: {
              type: "STRING",
              value: "me",
            },
            extensions: null,
          },
        ],
      },
      attributes: [
        {
          id: "message-attribute-id",
          key: "message",
          type: "STRING",
        },
      ],
      display_data: {
        label: "Gmail New Message Trigger",
        position: {
          x: 100,
          y: 200,
        },
        z_index: 1,
        icon: "gmail",
        color: "#EA4335",
      },
    },
  ],
  assertions: ["triggers/gmail_new_gmail_message.py"],
};
