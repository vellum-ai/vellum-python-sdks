export default {
  workflow_raw_data: {
    nodes: [
      {
        id: "simple-node",
        type: "GENERIC",
        label: "Simple Node",
        display_data: null,
        base: {
          name: "BaseNode",
          module: ["vellum", "workflows", "nodes", "bases", "base"],
        },
        definition: {
          name: "SimpleNode",
          module: ["testing", "nodes", "simple_node"],
        },
        trigger: {
          id: "simple-target",
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        ports: [
          {
            id: "simple-default-port-id",
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
          name: "final_output",
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
        display_data: null,
        base: {
          name: "FinalOutputNode",
          module: [
            "vellum",
            "workflows",
            "nodes",
            "displayable",
            "final_output_node",
            "node",
          ],
        },
        definition: {
          name: "FinalOutput",
          module: ["testing", "nodes", "final_output"],
        },
        trigger: {
          id: "final-output-target",
          merge_behavior: "AWAIT_ANY",
        },
        ports: [],
        outputs: [],
      },
    ],
    edges: [
      {
        id: "edge-1",
        source_node_id: "manual-trigger-id",
        source_handle_id: "manual-trigger-id",
        target_node_id: "simple-node",
        target_handle_id: "simple-target",
        type: "DEFAULT",
      },
      {
        id: "edge-2",
        source_node_id: "simple-node",
        source_handle_id: "simple-default-port-id",
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
      id: "final-output-var-id",
      key: "final_output",
      type: "STRING",
    },
  ],
  triggers: [
    {
      id: "manual-trigger-id",
      type: "MANUAL",
      attributes: [],
      definition: null,
      display_data: {
        label: "Manual Trigger",
        position: {
          x: 0.0,
          y: 0.0,
        },
        z_index: 0,
        icon: null,
        color: null,
        comment: null,
      },
    },
  ],
  assertions: ["workflow.py", "triggers/manual_trigger.py"],
};
