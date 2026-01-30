import { v4 as uuidv4 } from "uuid";

const outputVariableId = uuidv4();
const outputNodeId = uuidv4();
const outputInputId = uuidv4();
const outputHandleId = uuidv4();
const entrypointNodeId = uuidv4();
const entrypointHandleId = uuidv4();

const subworkflowNodeId = uuidv4();
const subworkflowSourceHandleId = uuidv4();
const subworkflowTargetHandleId = uuidv4();
const subworkflowOutputId = uuidv4();
const subworkflowInputsAttributeId = uuidv4();
const subworkflowInputId = uuidv4();

const workflowInputVariableId = uuidv4();

export default {
  input_variables: [
    {
      id: workflowInputVariableId,
      key: "user_data",
      type: "JSON",
      required: true,
      default: null,
      extensions: {},
    },
  ],
  output_variables: [
    {
      id: outputVariableId,
      key: "result",
      type: "STRING",
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
            "subworkflow_deployment_node",
            "node",
          ],
          name: "SubworkflowDeploymentNode",
        },
        data: {
          label: "Subworkflow Deployment Node",
          source_handle_id: subworkflowSourceHandleId,
          target_handle_id: subworkflowTargetHandleId,
          error_output_id: null,
          workflow_deployment_id: "test-deployment-id",
          release_tag: "LATEST",
          variant: "DEPLOYMENT",
        },
        definition: {
          module: ["test", "workflow", "subworkflow_deployment_node"],
          name: "SubworkflowDeploymentNodeNode",
        },
        id: subworkflowNodeId,
        inputs: [
          {
            id: subworkflowInputId,
            key: "user_name",
            value: {
              combinator: "OR",
              rules: [
                {
                  data: {
                    type: "STRING",
                    value: "",
                  },
                  type: "CONSTANT_VALUE",
                },
              ],
            },
          },
        ],
        attributes: [
          {
            id: subworkflowInputsAttributeId,
            name: "subworkflow_inputs",
            value: {
              type: "DICTIONARY_REFERENCE",
              entries: [
                {
                  key: "user_name",
                  value: {
                    type: "BINARY_EXPRESSION",
                    operator: "accessField",
                    lhs: {
                      type: "WORKFLOW_INPUT",
                      input_variable_id: workflowInputVariableId,
                    },
                    rhs: {
                      type: "CONSTANT_VALUE",
                      value: {
                        type: "STRING",
                        value: "name",
                      },
                    },
                  },
                },
              ],
            },
          },
        ],
        outputs: [
          {
            id: subworkflowOutputId,
            name: "result",
            type: "STRING",
          },
        ],
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
  assertions: [
    "nodes/subworkflow_deployment_node.py",
    "display/nodes/subworkflow_deployment_node.py",
  ],
};
