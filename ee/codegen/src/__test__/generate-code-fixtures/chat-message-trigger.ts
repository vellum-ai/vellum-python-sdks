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
        outputs: [
          {
            id: "bottom-output-id",
            name: "result",
            type: "STRING",
          },
        ],
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
        source_node_id: "chat-message-trigger",
        source_handle_id: "chat-message-trigger",
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
      id: "chat-message-trigger",
      type: "CHAT_MESSAGE",
      attributes: [
        {
          id: "message-attribute-id",
          key: "message",
          type: "JSON",
        },
      ],
      exec_config: {
        output: {
          type: "NODE_OUTPUT",
          node_id: "bottom-node",
          node_output_id: "bottom-output-id",
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
