import { v4 as uuidv4 } from "uuid";

const outputVariableId = uuidv4();
const outputNodeId = uuidv4();
const outputInputId = uuidv4();
const outputHandleId = uuidv4();
const entrypointNodeId = uuidv4();
const entrypointHandleId = uuidv4();

const outerMapNodeId = uuidv4();
const outerMapSourceHandleId = uuidv4();
const outerMapTargetHandleId = uuidv4();
const outerMapOutputNodeId = uuidv4();

const innerMapNodeId = uuidv4();
const innerMapSourceHandleId = uuidv4();
const innerMapTargetHandleId = uuidv4();
const innerMapOutputNodeId = uuidv4();
const sharedOutputId = uuidv4();

export default {
  input_variables: [],
  output_variables: [
    {
      id: outputVariableId,
      key: "result",
      type: "ARRAY",
    },
  ],
  state_variables: [],
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
        target_handle_id: outerMapTargetHandleId,
        target_node_id: outerMapNodeId,
        type: "DEFAULT",
      },
      {
        id: uuidv4(),
        source_handle_id: outerMapSourceHandleId,
        source_node_id: outerMapNodeId,
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
          label: "Outer Map",
          concurrency: 1,
          error_output_id: null,
          index_input_id: "outer-index",
          input_variables: [
            {
              id: "outer-items",
              key: "items",
              type: "ARRAY",
              required: true,
              default: null,
              extensions: {},
            },
            {
              id: "outer-item",
              key: "item",
              type: "STRING",
              required: true,
              default: null,
              extensions: {},
            },
            {
              id: "outer-index",
              key: "index",
              type: "NUMBER",
              required: true,
              default: null,
              extensions: {},
            },
          ],
          item_input_id: "outer-item",
          items_input_id: "outer-items",
          output_variables: [
            {
              id: "map-result",
              key: "result",
              type: "ARRAY",
            },
          ],
          source_handle_id: outerMapSourceHandleId,
          target_handle_id: outerMapTargetHandleId,
          variant: "INLINE",
          workflow_raw_data: {
            definition: {
              module: ["test", "workflow", "outer_map_workflow"],
              name: "OuterMapWorkflow",
            },
            edges: [
              {
                id: uuidv4(),
                source_handle_id: "inner-entry-src",
                source_node_id: "inner-entry-id",
                target_handle_id: innerMapTargetHandleId,
                target_node_id: innerMapNodeId,
                type: "DEFAULT",
              },
              {
                id: uuidv4(),
                source_handle_id: innerMapSourceHandleId,
                source_node_id: innerMapNodeId,
                target_handle_id: "inner-final-handle",
                target_node_id: outerMapOutputNodeId,
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
                    "core",
                    "map_node",
                    "node",
                  ],
                  name: "MapNode",
                },
                data: {
                  label: "Inner Map",
                  concurrency: 1,
                  error_output_id: null,
                  index_input_id: "inner-index",
                  input_variables: [
                    {
                      id: "inner-items",
                      key: "items",
                      type: "ARRAY",
                      required: true,
                      default: null,
                      extensions: {},
                    },
                    {
                      id: "inner-item",
                      key: "item",
                      type: "STRING",
                      required: true,
                      default: null,
                      extensions: {},
                    },
                    {
                      id: "inner-index",
                      key: "index",
                      type: "NUMBER",
                      required: true,
                      default: null,
                      extensions: {},
                    },
                  ],
                  item_input_id: "inner-item",
                  items_input_id: "inner-items",
                  output_variables: [
                    {
                      id: "inner-map-result",
                      key: "result",
                      type: "ARRAY",
                    },
                  ],
                  source_handle_id: innerMapSourceHandleId,
                  target_handle_id: innerMapTargetHandleId,
                  variant: "INLINE",
                  workflow_raw_data: {
                    definition: {
                      module: [
                        "test",
                        "workflow",
                        "outer_map_workflow",
                        "inner_map_workflow",
                      ],
                      name: "InnerMapWorkflow",
                    },
                    edges: [
                      {
                        id: uuidv4(),
                        source_handle_id: "inner-inner-entry-src",
                        source_node_id: "inner-inner-entry-id",
                        target_handle_id: "inner-inner-final-handle",
                        target_node_id: innerMapOutputNodeId,
                        type: "DEFAULT",
                      },
                    ],
                    nodes: [
                      {
                        base: null,
                        data: {
                          label: "Entrypoint Node",
                          source_handle_id: "inner-inner-entry-src",
                        },
                        definition: null,
                        id: "inner-inner-entry-id",
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
                          name: "inner-result",
                          node_input_id: "inner-inner-output-input-id",
                          output_id: sharedOutputId, // identical output id to outer
                          output_type: "STRING",
                          target_handle_id: "inner-inner-final-handle",
                        },
                        definition: {
                          module: [
                            "test",
                            "workflow",
                            "outer_map_workflow",
                            "inner_map_workflow",
                            "final_output",
                          ],
                          name: "InnerFinalOutput",
                        },
                        id: innerMapOutputNodeId,
                        inputs: [
                          {
                            id: "inner-inner-output-input-id",
                            key: "node_input",
                            value: {
                              combinator: "OR",
                              rules: [
                                {
                                  data: {
                                    type: "STRING",
                                    value: "leaf",
                                  },
                                  type: "CONSTANT_VALUE",
                                },
                              ],
                            },
                          },
                        ],
                        outputs: [
                          {
                            id: sharedOutputId,
                            name: "value",
                            type: "STRING",
                            value: {
                              type: "CONSTANT_VALUE",
                              value: {
                                type: "STRING",
                                value: "leaf",
                              },
                            },
                          },
                        ],
                        ports: [],
                        trigger: {
                          id: "inner-inner-final-handle",
                          merge_behavior: "AWAIT_ANY",
                        },
                        type: "TERMINAL",
                      },
                      {
                        base: null,
                        data: {
                          label: "Final Output",
                          target_handle_id: "inner-inner-final-handle",
                          output_id: sharedOutputId,
                          output_type: "STRING",
                          name: "inner-inner-result",
                          node_input_id: "inner-inner-output-input-id",
                        },
                        definition: null,
                        id: innerMapOutputNodeId,
                        inputs: [
                          {
                            id: "inner-inner-output-input-id",
                            key: "node_input",
                            value: {
                              combinator: "OR",
                              rules: [
                                {
                                  data: {
                                    type: "STRING",
                                    value: "leaf",
                                  },
                                  type: "CONSTANT_VALUE",
                                },
                              ],
                            },
                          },
                        ],
                        type: "TERMINAL",
                      },
                    ],
                    output_values: [
                      {
                        output_variable_id: "inner-map-result",
                        value: {
                          node_id: innerMapOutputNodeId,
                          node_output_id: sharedOutputId,
                          type: "NODE_OUTPUT",
                        },
                      },
                    ],
                  },
                },
                definition: {
                  module: [
                    "test",
                    "workflow",
                    "outer_map_workflow",
                    "inner_map_workflow",
                  ],
                  name: "InnerMapNode",
                },
                id: innerMapNodeId,
                inputs: [
                  {
                    id: "inner-items",
                    key: "items",
                    value: {
                      combinator: "OR",
                      rules: [
                        {
                          data: {
                            type: "JSON",
                            value: ["a", "b"],
                          },
                          type: "CONSTANT_VALUE",
                        },
                      ],
                    },
                  },
                ],
                ports: [
                  {
                    id: innerMapSourceHandleId,
                    name: "default",
                    type: "DEFAULT",
                  },
                ],
                trigger: {
                  id: innerMapTargetHandleId,
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
                  label: "Final Output",
                  name: "inner-map-result",
                  node_input_id: "inner-output-input-id",
                  output_id: sharedOutputId, // identical output id to inner final output
                  output_type: "STRING",
                  target_handle_id: "inner-final-handle",
                },
                definition: {
                  module: [
                    "test",
                    "workflow",
                    "outer_map_workflow",
                    "final_output",
                  ],
                  name: "OuterInnerFinalOutput",
                },
                id: outerMapOutputNodeId,
                inputs: [
                  {
                    id: "inner-output-input-id",
                    key: "node_input",
                    value: {
                      combinator: "OR",
                      rules: [
                        {
                          data: {
                            node_id: innerMapNodeId,
                            output_id: "inner-map-result",
                          },
                          type: "NODE_OUTPUT",
                        },
                      ],
                    },
                  },
                ],
                outputs: [
                  {
                    id: sharedOutputId,
                    name: "value",
                    type: "STRING",
                    value: {
                      node_id: innerMapNodeId,
                      node_output_id: "inner-map-result",
                      type: "NODE_OUTPUT",
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
                output_variable_id: "map-result",
                value: {
                  node_id: outerMapOutputNodeId,
                  node_output_id: sharedOutputId,
                  type: "NODE_OUTPUT",
                },
              },
            ],
          },
        },
        definition: {
          module: ["test", "workflow", "outer_map_workflow"],
          name: "OuterMapNode",
        },
        id: outerMapNodeId,
        inputs: [
          {
            id: "outer-items",
            key: "items",
            value: {
              combinator: "OR",
              rules: [
                {
                  data: {
                    type: "JSON",
                    value: [1],
                  },
                  type: "CONSTANT_VALUE",
                },
              ],
            },
          },
        ],
        ports: [
          {
            id: outerMapSourceHandleId,
            name: "default",
            type: "DEFAULT",
          },
        ],
        trigger: {
          id: outerMapTargetHandleId,
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
                    node_id: outerMapNodeId,
                    output_id: "map-result",
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
              node_id: outerMapNodeId,
              node_output_id: "map-result",
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
  assertions: ["nodes/outer_map_workflow/nodes/inner_map_workflow/__init__.py"],
};
