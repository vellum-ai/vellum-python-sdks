import { v4 as uuidv4 } from "uuid";

const outputVariableId = uuidv4();
const outputNodeId = uuidv4();
const outputInputId = uuidv4();
const outputHandleId = uuidv4();
const entrypointNodeId = uuidv4();
const entrypointHandleId = uuidv4();

const parentStateVariableId = uuidv4();
const innerStateVariableId = uuidv4();

const subworkflowNodeId = uuidv4();
const subworkflowSourceHandleId = uuidv4();
const subworkflowTargetHandleId = uuidv4();
const subworkflowOutputNodeId = uuidv4();
const subworkflowOutputId = uuidv4();

export default {
  input_variables: [],
  output_variables: [
    {
      id: outputVariableId,
      key: "result",
      type: "STRING",
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
        target_handle_id: subworkflowTargetHandleId,
        target_node_id: subworkflowNodeId,
        type: "DEFAULT",
      },
      {
        id: uuidv4(),
        source_handle_id: subworkflowSourceHandleId,
        source_node_id: subworkflowNodeId,
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
          module: [
            "vellum",
            "workflows",
            "nodes",
            "displayable",
            "inline_subworkflow_node",
            "node",
          ],
          name: "InlineSubworkflowNode",
        },
        data: {
          label: "Subworkflow With State",
          error_output_id: null,
          input_variables: [],
          output_variables: [
            {
              id: subworkflowOutputId,
              key: "subworkflow_result",
              type: "STRING",
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
          source_handle_id: subworkflowSourceHandleId,
          target_handle_id: subworkflowTargetHandleId,
          variant: "INLINE",
          workflow_raw_data: {
            definition: {
              module: ["test", "workflow", "subworkflow_with_state"],
              name: "SubworkflowWithState",
            },
            edges: [
              {
                id: uuidv4(),
                source_handle_id: "inner-entry-src",
                source_node_id: "inner-entry-id",
                target_handle_id: "inner-final-handle",
                target_node_id: subworkflowOutputNodeId,
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
                  name: "subworkflow_result",
                  node_input_id: "inner-output-input-id",
                  output_id: subworkflowOutputId,
                  output_type: "STRING",
                  target_handle_id: "inner-final-handle",
                },
                definition: {
                  module: [
                    "test",
                    "workflow",
                    "subworkflow_with_state",
                    "final_output",
                  ],
                  name: "SubworkflowFinalOutput",
                },
                id: subworkflowOutputNodeId,
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
                            value: "result from subworkflow",
                          },
                          type: "CONSTANT_VALUE",
                        },
                      ],
                    },
                  },
                ],
                outputs: [
                  {
                    id: subworkflowOutputId,
                    name: "value",
                    type: "STRING",
                    value: {
                      type: "CONSTANT_VALUE",
                      value: {
                        type: "STRING",
                        value: "result from subworkflow",
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
                output_variable_id: subworkflowOutputId,
                value: {
                  node_id: subworkflowOutputNodeId,
                  node_output_id: subworkflowOutputId,
                  type: "NODE_OUTPUT",
                },
              },
            ],
          },
        },
        definition: {
          module: ["test", "workflow", "subworkflow_with_state"],
          name: "SubworkflowWithStateNode",
        },
        id: subworkflowNodeId,
        inputs: [],
        ports: [
          {
            id: subworkflowSourceHandleId,
            name: "default",
            type: "DEFAULT",
          },
        ],
        trigger: {
          id: subworkflowTargetHandleId,
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        type: "SUBWORKFLOW",
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
          output_type: "STRING",
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
                    node_id: subworkflowNodeId,
                    output_id: subworkflowOutputId,
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
            type: "STRING",
            value: {
              node_id: subworkflowNodeId,
              node_output_id: subworkflowOutputId,
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
  assertions: ["state.py", "nodes/subworkflow_with_state/state.py"],
};
