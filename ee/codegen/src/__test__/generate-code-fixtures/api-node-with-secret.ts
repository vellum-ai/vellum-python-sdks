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
        id: "api-node-with-secret",
        type: "API",
        data: {
          label: "API Request Node",
          method_input_id: "method-input-id",
          url_input_id: "url-input-id",
          body_input_id: "body-input-id",
          authorization_type_input_id: "auth-type-input-id",
          bearer_token_value_input_id: "bearer-token-input-id",
          api_key_header_key_input_id: "api-key-header-key-input-id",
          api_key_header_value_input_id: "api-key-header-value-input-id",
          additional_headers: [
            {
              header_key_input_id: "content-type-key-input-id",
              header_value_input_id: "content-type-value-input-id",
            },
          ],
          text_output_id: "text-output-id",
          json_output_id: "json-output-id",
          status_code_output_id: "status-code-output-id",
          error_output_id: null,
          target_handle_id: "api-node-target",
          source_handle_id: "api-node-source",
        },
        inputs: [
          {
            id: "url-input-id",
            key: "url",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "https://api.example.com/v1/test",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "method-input-id",
            key: "method",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "POST",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "body-input-id",
            key: "body",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "JSON",
                    value: {
                      input: "test-data",
                    },
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "auth-type-input-id",
            key: "authorization_type",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "BEARER_TOKEN",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "bearer-token-input-id",
            key: "bearer_token_value",
            value: {
              rules: [
                {
                  type: "WORKSPACE_SECRET",
                  data: {
                    type: "STRING",
                    workspace_secret_id: "test-workspace-secret-id",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "api-key-header-key-input-id",
            key: "api_key_header_key",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "Authorization",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "api-key-header-value-input-id",
            key: "api_key_header_value",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "content-type-key-input-id",
            key: "additional_header_key",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "Content-Type",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "content-type-value-input-id",
            key: "additional_header_value",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "application/json",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
        display_data: {
          position: {
            x: 500,
            y: 200,
          },
          z_index: 1,
          comment: null,
          width: 330.0,
          height: 96.0,
          icon: null,
          color: null,
        },
        base: null,
        definition: {
          name: "ApiWithSecret",
          module: ["testing", "nodes", "api_with_secret"],
        },
        trigger: {
          id: "api-node-target",
          merge_behavior: "AWAIT_ANY",
        },
        ports: [
          {
            id: "api-node-source",
            name: "default",
            type: "DEFAULT",
          },
        ],
        adornments: null,
        outputs: null,
        attributes: [
          {
            id: "timeout-attribute-id",
            name: "timeout",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "NUMBER",
                value: 60.0,
              },
            },
          },
        ],
      },
      {
        id: "terminal-node",
        type: "TERMINAL",
        data: {
          label: "Final Output",
          name: "result",
          target_handle_id: "terminal-target",
          output_id: "terminal-output-id",
          output_type: "JSON",
          node_input_id: "terminal-node-input-id",
        },
        inputs: [
          {
            id: "terminal-node-input-id",
            key: "node_input",
            value: {
              rules: [
                {
                  type: "NODE_OUTPUT",
                  data: {
                    node_id: "api-node-with-secret",
                    output_id: "json-output-id",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
        display_data: {
          position: {
            x: 1000,
            y: 200,
          },
          z_index: 2,
          comment: null,
          width: 330.0,
          height: 96.0,
          icon: null,
          color: null,
        },
        base: null,
        definition: {
          name: "UseApiWithSecret",
          module: ["testing", "nodes", "use_api_with_secret"],
        },
        trigger: {
          id: "terminal-target",
          merge_behavior: "AWAIT_ANY",
        },
        outputs: [
          {
            id: "terminal-output-id",
            name: "value",
            type: "JSON",
            value: {
              type: "NODE_OUTPUT",
              node_id: "api-node-with-secret",
              node_output_id: "json-output-id",
            },
          },
        ],
      },
    ],
    edges: [
      {
        id: "edge-1",
        source_node_id: "entrypoint-node",
        source_handle_id: "entrypoint-source",
        target_node_id: "api-node-with-secret",
        target_handle_id: "api-node-target",
        type: "DEFAULT",
      },
      {
        id: "edge-2",
        source_node_id: "api-node-with-secret",
        source_handle_id: "api-node-source",
        target_node_id: "terminal-node",
        target_handle_id: "terminal-target",
        type: "DEFAULT",
      },
    ],
  },
  input_variables: [],
  output_variables: [
    {
      id: "terminal-output-id",
      key: "result",
      type: "JSON",
    },
  ],
  assertions: [
    "nodes/api_with_secret.py",
    "nodes/use_api_with_secret.py",
  ],
};
