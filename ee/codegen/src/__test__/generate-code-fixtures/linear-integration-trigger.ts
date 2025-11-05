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
        source_node_id: "linear-integration-trigger",
        source_handle_id: "linear-integration-trigger",
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
  ],
  assertions: ["workflow.py", "triggers/linear_comment_event_trigger.py"],
};
