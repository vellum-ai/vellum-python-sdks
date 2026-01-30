export default {
  input_variables: [
    {
      id: "workflow-input-data-id",
      key: "data",
      type: "JSON",
      required: true,
      default: null,
      extensions: {},
    },
  ],
  output_variables: [
    {
      id: "workflow-output-result-id",
      key: "result",
      type: "ARRAY",
    },
  ],
  workflow_raw_data: {
    definition: {
      module: ["test", "workflow"],
      name: "Workflow",
    },
    edges: [
      {
        id: "edge-entrypoint-to-map",
        source_handle_id: "entrypoint-source-handle",
        source_node_id: "entrypoint-node-id",
        target_handle_id: "map-target-handle",
        target_node_id: "map-node-id",
        type: "DEFAULT",
      },
      {
        id: "edge-map-to-output",
        source_handle_id: "map-source-handle",
        source_node_id: "map-node-id",
        target_handle_id: "output-target-handle",
        target_node_id: "output-node-id",
        type: "DEFAULT",
      },
    ],
    nodes: [
      {
        base: null,
        data: {
          label: "Entrypoint Node",
          source_handle_id: "entrypoint-source-handle",
        },
        definition: null,
        id: "entrypoint-node-id",
        inputs: [],
        type: "ENTRYPOINT",
      },
      {
        base: {
          module: ["vellum", "workflows", "nodes", "core", "map_node", "node"],
          name: "MapNode",
        },
        data: {
          label: "Map Node",
          concurrency: 1,
          error_output_id: null,
          index_input_id: "map-index-input-id",
          input_variables: [
            {
              id: "map-items-input-id",
              key: "items",
              type: "ARRAY",
              required: true,
              default: null,
              extensions: {},
            },
            {
              id: "map-item-input-id",
              key: "item",
              type: "JSON",
              required: true,
              default: null,
              extensions: {},
            },
            {
              id: "map-index-input-id",
              key: "index",
              type: "NUMBER",
              required: true,
              default: null,
              extensions: {},
            },
          ],
          item_input_id: "map-item-input-id",
          items_input_id: "map-items-input-id",
          output_variables: [
            {
              id: "map-output-id",
              key: "map_result",
              type: "ARRAY",
            },
          ],
          source_handle_id: "map-source-handle",
          target_handle_id: "map-target-handle",
          variant: "INLINE",
          workflow_raw_data: {
            definition: {
              module: ["test", "workflow", "map_node"],
              name: "MapNodeSubworkflow",
            },
            edges: [
              {
                id: "inner-edge-entrypoint-to-final",
                source_handle_id: "inner-entrypoint-source",
                source_node_id: "inner-entrypoint-id",
                target_handle_id: "inner-final-handle",
                target_node_id: "inner-final-output-id",
                type: "DEFAULT",
              },
            ],
            nodes: [
              {
                base: null,
                data: {
                  label: "Entrypoint Node",
                  source_handle_id: "inner-entrypoint-source",
                },
                definition: null,
                id: "inner-entrypoint-id",
                inputs: [],
                type: "ENTRYPOINT",
              },
              {
                base: {
                  module: [
                    "vellum",
                    "workflows",
                    "nodes",
                    "displayable",
                    "final_output_node",
                    "node",
                  ],
                  name: "FinalOutputNode",
                },
                data: {
                  label: "Final Output",
                  name: "map_result",
                  node_input_id: "inner-output-input-id",
                  output_id: "map-output-id",
                  output_type: "STRING",
                  target_handle_id: "inner-final-handle",
                },
                definition: {
                  module: ["test", "workflow", "map_node", "final_output"],
                  name: "MapFinalOutput",
                },
                id: "inner-final-output-id",
                inputs: [
                  {
                    id: "inner-output-input-id",
                    key: "node_input",
                    value: {
                      combinator: "OR",
                      rules: [
                        {
                          data: {
                            type: "STRING",
                            value: "result from map",
                          },
                          type: "CONSTANT_VALUE",
                        },
                      ],
                    },
                  },
                ],
                outputs: [
                  {
                    id: "map-output-id",
                    name: "value",
                    type: "STRING",
                    value: {
                      type: "CONSTANT_VALUE",
                      value: {
                        type: "STRING",
                        value: "result from map",
                      },
                    },
                  },
                ],
                ports: [],
                trigger: {
                  id: "inner-final-handle",
                  merge_behavior: "AWAIT_ANY",
                },
                type: "TERMINAL",
              },
            ],
            output_values: [
              {
                output_variable_id: "map-output-id",
                value: {
                  node_id: "inner-final-output-id",
                  node_output_id: "map-output-id",
                  type: "NODE_OUTPUT",
                },
              },
            ],
          },
        },
        definition: {
          module: ["test", "workflow", "map_node"],
          name: "MapNodeNode",
        },
        id: "map-node-id",
        inputs: [
          {
            id: "map-items-input-id",
            key: "items",
            value: {
              combinator: "OR",
              rules: [
                {
                  data: {
                    type: "JSON",
                    value: [],
                  },
                  type: "CONSTANT_VALUE",
                },
              ],
            },
          },
        ],
        attributes: [
          {
            id: "map-items-attribute-id",
            name: "items",
            value: {
              type: "BINARY_EXPRESSION",
              operator: "accessField",
              lhs: {
                type: "WORKFLOW_INPUT",
                input_variable_id: "workflow-input-data-id",
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "items",
                },
              },
            },
          },
        ],
        ports: [
          {
            id: "map-source-handle",
            name: "default",
            type: "DEFAULT",
          },
        ],
        trigger: {
          id: "map-target-handle",
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        type: "MAP",
      },
      {
        base: {
          module: [
            "vellum",
            "workflows",
            "nodes",
            "displayable",
            "final_output_node",
            "node",
          ],
          name: "FinalOutputNode",
        },
        data: {
          label: "Workflow Output",
          name: "result",
          node_input_id: "output-input-id",
          output_id: "workflow-output-result-id",
          output_type: "ARRAY",
          target_handle_id: "output-target-handle",
        },
        definition: {
          module: ["test", "workflow", "final_output"],
          name: "WorkflowFinalOutput",
        },
        id: "output-node-id",
        inputs: [
          {
            id: "output-input-id",
            key: "node_input",
            value: {
              combinator: "OR",
              rules: [
                {
                  data: {
                    node_id: "map-node-id",
                    output_id: "map-output-id",
                  },
                  type: "NODE_OUTPUT",
                },
              ],
            },
          },
        ],
        outputs: [
          {
            id: "workflow-output-result-id",
            name: "value",
            type: "ARRAY",
            value: {
              node_id: "map-node-id",
              node_output_id: "map-output-id",
              type: "NODE_OUTPUT",
            },
          },
        ],
        ports: [],
        trigger: {
          id: "output-target-handle",
          merge_behavior: "AWAIT_ANY",
        },
        type: "TERMINAL",
      },
    ],
    output_values: [
      {
        output_variable_id: "workflow-output-result-id",
        value: {
          node_id: "output-node-id",
          node_output_id: "workflow-output-result-id",
          type: "NODE_OUTPUT",
        },
      },
    ],
  },
  assertions: [
    "nodes/map_node/__init__.py",
    "display/nodes/map_node/__init__.py",
  ],
};
