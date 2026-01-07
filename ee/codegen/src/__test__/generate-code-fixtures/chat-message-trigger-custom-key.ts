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
    output_values: [
      {
        output_variable_id: "workflow-output-variable-id",
        value: {
          type: "NODE_OUTPUT",
          node_id: "some-node",
          node_output_id: "some-output-id",
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
  state_variables: [
    {
      id: "messages-state-variable-id",
      key: "messages",
      type: "CHAT_HISTORY",
    },
  ],
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
          type: "WORKFLOW_OUTPUT",
          output_variable_id: "workflow-output-variable-id",
        },
        state: {
          state_variable_id: "messages-state-variable-id",
        },
      },
      display_data: {
        label: "Custom State Trigger",
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
  assertions: ["workflow.py", "triggers/custom_state_trigger.py"],
};
