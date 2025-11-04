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
        source_node_id: "8b215007-ddb0-410f-a16d-c09815e3445d",
        source_handle_id: "8b215007-ddb0-410f-a16d-c09815e3445d",
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
      id: "8b215007-ddb0-410f-a16d-c09815e3445d",
      type: "SCHEDULED",
      cron: "* * * * *",
      timezone: "UTC",
      attributes: [],
      definition: null,
      display_data: {
        label: "Scheduled Trigger",
        position: {
          x: 0.0,
          y: 0.0,
        },
        z_index: 0,
        icon: null,
        color: null,
      },
    },
  ],
  assertions: ["workflow.py", "triggers/scheduled.py"],
};
