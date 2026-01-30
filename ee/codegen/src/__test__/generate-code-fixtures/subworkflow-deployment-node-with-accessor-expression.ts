export default {
  input_variables: [
    {
      id: "workflow-input-user-data-id",
      key: "user_data",
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
        id: "edge-entrypoint-to-subworkflow",
        source_handle_id: "entrypoint-source-handle",
        source_node_id: "entrypoint-node-id",
        target_handle_id: "subworkflow-target-handle",
        target_node_id: "subworkflow-node-id",
        type: "DEFAULT",
      },
      {
        id: "edge-subworkflow-to-output",
        source_handle_id: "subworkflow-source-handle",
        source_node_id: "subworkflow-node-id",
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
          source_handle_id: "subworkflow-source-handle",
          target_handle_id: "subworkflow-target-handle",
          error_output_id: null,
          workflow_deployment_id: "test-deployment-id",
          release_tag: "LATEST",
          variant: "DEPLOYMENT",
        },
        definition: {
          module: ["test", "workflow", "subworkflow_deployment_node"],
          name: "SubworkflowDeploymentNodeNode",
        },
        id: "subworkflow-node-id",
        inputs: [
          {
            id: "subworkflow-input-user-name-id",
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
            id: "subworkflow-inputs-attribute-id",
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
                      input_variable_id: "workflow-input-user-data-id",
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
            id: "subworkflow-output-result-id",
            name: "result",
            type: "STRING",
          },
        ],
        ports: [
          {
            id: "subworkflow-source-handle",
            name: "default",
            type: "DEFAULT",
          },
        ],
        trigger: {
          id: "subworkflow-target-handle",
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
          node_input_id: "output-input-id",
          output_id: "workflow-output-result-id",
          output_type: "STRING",
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
                    node_id: "subworkflow-node-id",
                    output_id: "subworkflow-output-result-id",
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
            type: "STRING",
            value: {
              node_id: "subworkflow-node-id",
              node_output_id: "subworkflow-output-result-id",
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
  assertions: ["nodes/subworkflow_deployment_node.py"],
};
