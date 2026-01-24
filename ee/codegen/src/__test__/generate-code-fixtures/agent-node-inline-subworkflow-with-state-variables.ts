import { v4 as uuidv4 } from "uuid";

const outputVariableId = uuidv4();
const outputNodeId = uuidv4();
const outputInputId = uuidv4();
const outputHandleId = uuidv4();
const entrypointNodeId = uuidv4();
const entrypointHandleId = uuidv4();

const parentStateVariableId = uuidv4();
const innerStateVariableId = uuidv4();

const agentNodeId = uuidv4();
const agentNodeSourceHandleId = uuidv4();
const agentNodeTargetHandleId = uuidv4();

const subworkflowOutputId = uuidv4();
const subworkflowOutputNodeId = uuidv4();

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
        target_handle_id: agentNodeTargetHandleId,
        target_node_id: agentNodeId,
        type: "DEFAULT",
      },
      {
        id: uuidv4(),
        source_handle_id: agentNodeSourceHandleId,
        source_node_id: agentNodeId,
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
        id: agentNodeId,
        type: "GENERIC",
        label: "Agent With Subworkflow Tool",
        base: {
          name: "ToolCallingNode",
          module: [
            "vellum",
            "workflows",
            "nodes",
            "displayable",
            "tool_calling_node",
          ],
        },
        definition: {
          module: ["test", "workflow", "agent_with_subworkflow_tool"],
          name: "AgentWithSubworkflowToolNode",
        },
        trigger: {
          id: agentNodeTargetHandleId,
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        ports: [
          {
            id: agentNodeSourceHandleId,
            name: "default",
            type: "DEFAULT",
          },
        ],
        attributes: [
          {
            id: uuidv4(),
            name: "ml_model",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "gpt-4o-mini" },
            },
          },
          {
            id: uuidv4(),
            name: "blocks",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: [
                  {
                    state: null,
                    blocks: [
                      {
                        state: null,
                        blocks: [
                          {
                            text: "You are a helpful assistant",
                            state: null,
                            block_type: "PLAIN_TEXT",
                            cache_config: null,
                          },
                        ],
                        block_type: "RICH_TEXT",
                        cache_config: null,
                      },
                    ],
                    chat_role: "SYSTEM",
                    block_type: "CHAT_MESSAGE",
                    chat_source: null,
                    cache_config: null,
                    chat_message_unterminated: null,
                  },
                ],
              },
            },
          },
          {
            id: uuidv4(),
            name: "functions",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: [
                  {
                    type: "INLINE_WORKFLOW",
                    name: "subworkflow_with_state",
                    description: "A subworkflow tool with state variables",
                    exec_config: {
                      workflow_raw_data: {
                        definition: {
                          module: [
                            "test",
                            "workflow",
                            "agent_with_subworkflow_tool",
                            "subworkflow_with_state",
                          ],
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
                                "agent_with_subworkflow_tool",
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
                                        value: "result from subworkflow tool",
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
                                    value: "result from subworkflow tool",
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
                    },
                  },
                ],
              },
            },
          },
          {
            id: uuidv4(),
            name: "prompt_inputs",
            value: {
              type: "DICTIONARY_REFERENCE",
              entries: [],
            },
          },
        ],
        outputs: [
          {
            id: "agent-text-output-id",
            name: "text",
            type: "STRING",
          },
        ],
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
                    node_id: agentNodeId,
                    output_id: "agent-text-output-id",
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
              node_id: agentNodeId,
              node_output_id: "agent-text-output-id",
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
  assertions: [
    "state.py",
    "nodes/agent_with_subworkflow_tool/subworkflow_with_state/state.py",
  ],
};
