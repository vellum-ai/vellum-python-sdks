export default {
  workflow_raw_data: {
    nodes: [
      {
        id: "some-node",
        type: "GENERIC",
        label: "Some Node",
        display_data: null,
        base: {
          name: "BaseNode",
          module: ["vellum", "workflows", "nodes", "bases", "base"],
        },
        definition: {
          name: "SomeNode",
          module: ["testing", "nodes", "some_node"],
        },
        trigger: {
          id: "some-target",
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        ports: [
          {
            id: "some-default-port-id",
            name: "default",
            type: "DEFAULT",
          },
        ],
        outputs: [
          {
            id: "some-output-id",
            name: "result",
            type: "STRING",
          },
        ],
        attributes: [],
      },
    ],
    edges: [
      {
        id: "edge-2",
        source_node_id: "chat-message-trigger",
        source_handle_id: "chat-message-trigger",
        target_node_id: "some-node",
        target_handle_id: "some-target",
        type: "DEFAULT",
      },
    ],
    output_values: [],
  },
  input_variables: [],
  output_variables: [],
  triggers: [
    {
      id: "chat-message-trigger",
      type: "CHAT_MESSAGE",
      attributes: [
        {
          id: "message-attribute-id",
          key: "message",
          type: "STRING",
          required: true,
          schema: null,
          default: {
            type: "STRING",
            value: "Hello",
          },
          extensions: null,
          definition: null,
        },
      ],
      exec_config: {
        output: {
          type: "NODE_OUTPUT",
          node_id: "some-node",
          node_output_id: "some-output-id",
        },
      },
      display_data: {
        label: "Chat Message",
        position: {
          x: 100,
          y: 200,
        },
        z_index: 1,
        icon: "vellum:icon:message",
        color: "blue",
      },
    },
  ],
  assertions: ["workflow.py", "triggers/chat_message.py"],
};
