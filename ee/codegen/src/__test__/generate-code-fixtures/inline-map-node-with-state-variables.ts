import { v4 as uuidv4 } from "uuid";

const outputVariableId = uuidv4();
const outputNodeId = uuidv4();
const outputInputId = uuidv4();
const outputHandleId = uuidv4();
const entrypointNodeId = uuidv4();
const entrypointHandleId = uuidv4();

const parentStateVariableId = uuidv4();
const innerStateVariableId = uuidv4();

const mapNodeId = uuidv4();
const mapSourceHandleId = uuidv4();
const mapTargetHandleId = uuidv4();
const mapOutputNodeId = uuidv4();
const mapOutputId = uuidv4();

export default {
  input_variables: [],
  output_variables: [
    {
      id: outputVariableId,
      key: "result",
      type: "ARRAY",
    },
  ],
  state_variables: [
    {
      id: parentStateVariableId,
      key: "parent_counter",
      type: "NUMBER",
      default: {
        type: "NUMBER",
        value: 0,
      },
    },
  ],
  workflow_raw_data: {
    definition: {
      module: ["test", "workflow"],
      name: "Workflow",
    },
    edges: [
      {
        id: uuidv4(),
        source_handle_id: entrypointHandleId,
        source_node_id: entrypointNodeId,
        target_handle_id: mapTargetHandleId,
        target_node_id: mapNodeId,
        type: "DEFAULT",
      },
      {
        id: uuidv4(),
        source_handle_id: mapSourceHandleId,
        source_node_id: mapNodeId,
        target_handle_id: outputHandleId,
        target_node_id: outputNodeId,
        type: "DEFAULT",
      },
    ],
    nodes: [
      {
        base: null,
        data: {
          label: "Entrypoint Node",
          source_handle_id: entrypointHandleId,
        },
        definition: null,
        id: entrypointNodeId,
        inputs: [],
        type: "ENTRYPOINT",
      },
      {
        base: {
          module: ["vellum", "workflows", "nodes", "core", "map_node", "node"],
          name: "MapNode",
        },
        data: {
          label: "Map With State",
          concurrency: 1,
          error_output_id: null,
          index_input_id: "map-index",
          input_variables: [
            {
              id: "map-items",
              key: "items",
              type: "ARRAY",
              required: true,
              default: null,
              extensions: {},
            },
            {
              id: "map-item",
              key: "item",
              type: "STRING",
              required: true,
              default: null,
              extensions: {},
            },
            {
              id: "map-index",
              key: "index",
              type: "NUMBER",
              required: true,
              default: null,
              extensions: {},
            },
          ],
          item_input_id: "map-item",
          items_input_id: "map-items",
          output_variables: [
            {
              id: mapOutputId,
              key: "map_result",
              type: "ARRAY",
            },
          ],
          state_variables: [
            {
              id: innerStateVariableId,
              key: "inner_counter",
              type: "NUMBER",
              default: {
                type: "NUMBER",
                value: 0,
              },
            },
          ],
          source_handle_id: mapSourceHandleId,
          target_handle_id: mapTargetHandleId,
          variant: "INLINE",
          workflow_raw_data: {
            definition: {
              module: ["test", "workflow", "map_with_state"],
              name: "MapWithState",
            },
            edges: [
              {
                id: uuidv4(),
                source_handle_id: "inner-entry-src",
                source_node_id: "inner-entry-id",
                target_handle_id: "inner-final-handle",
                target_node_id: mapOutputNodeId,
                type: "DEFAULT",
              },
            ],
            nodes: [
              {
                base: null,
                data: {
                  label: "Entrypoint Node",
                  source_handle_id: "inner-entry-src",
                },
                definition: null,
                id: "inner-entry-id",
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
                  output_id: mapOutputId,
                  output_type: "STRING",
                  target_handle_id: "inner-final-handle",
                },
                definition: {
                  module: [
                    "test",
                    "workflow",
                    "map_with_state",
                    "final_output",
                  ],
                  name: "MapFinalOutput",
                },
                id: mapOutputNodeId,
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
                    id: mapOutputId,
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
                output_variable_id: mapOutputId,
                value: {
                  node_id: mapOutputNodeId,
                  node_output_id: mapOutputId,
                  type: "NODE_OUTPUT",
                },
              },
            ],
          },
        },
        definition: {
          module: ["test", "workflow", "map_with_state"],
          name: "MapWithStateNode",
        },
        id: mapNodeId,
        inputs: [
          {
            id: "map-items",
            key: "items",
            value: {
              combinator: "OR",
              rules: [
                {
                  data: {
                    type: "JSON",
                    value: ["a", "b", "c"],
                  },
                  type: "CONSTANT_VALUE",
                },
              ],
            },
          },
        ],
        ports: [
          {
            id: mapSourceHandleId,
            name: "default",
            type: "DEFAULT",
          },
        ],
        trigger: {
          id: mapTargetHandleId,
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
          node_input_id: outputInputId,
          output_id: outputVariableId,
          output_type: "ARRAY",
          target_handle_id: outputHandleId,
        },
        definition: {
          module: ["test", "workflow", "final_output"],
          name: "WorkflowFinalOutput",
        },
        id: outputNodeId,
        inputs: [
          {
            id: outputInputId,
            key: "node_input",
            value: {
              combinator: "OR",
              rules: [
                {
                  data: {
                    node_id: mapNodeId,
                    output_id: mapOutputId,
                  },
                  type: "NODE_OUTPUT",
                },
              ],
            },
          },
        ],
        outputs: [
          {
            id: outputVariableId,
            name: "value",
            type: "ARRAY",
            value: {
              node_id: mapNodeId,
              node_output_id: mapOutputId,
              type: "NODE_OUTPUT",
            },
          },
        ],
        ports: [],
        trigger: {
          id: outputHandleId,
          merge_behavior: "AWAIT_ANY",
        },
        type: "TERMINAL",
      },
    ],
    output_values: [
      {
        output_variable_id: outputVariableId,
        value: {
          node_id: outputNodeId,
          node_output_id: outputVariableId,
          type: "NODE_OUTPUT",
        },
      },
    ],
  },
  assertions: ["state.py", "nodes/map_with_state/state.py"],
};
