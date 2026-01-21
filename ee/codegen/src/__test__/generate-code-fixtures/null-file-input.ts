export default {
  workflow_raw_data: {
    nodes: [
      {
        id: "7be676ae-b011-454b-aa59-0c26385a543c",
        type: "ENTRYPOINT",
        data: {
          label: "Entrypoint Node",
          source_handle_id: "3006c2ba-2638-4494-9154-9a716ab2af63",
        },
        inputs: [],
      },
      {
        id: "b1ede5dd-2c27-442f-bf59-77a87caf2184",
        type: "TERMINAL",
        data: {
          name: "final-output",
          label: "Final Output",
          target_handle_id: "2892f5b0-a6c9-4854-ac53-cf5e17b9ae16",
          output_id: "cff5b127-113b-42ed-aa08-d300ac3583c1",
          output_type: "DOCUMENT",
          node_input_id: "d8104087-048f-40db-bec8-2762a9eee6b0",
        },
        inputs: [
          {
            id: "d8104087-048f-40db-bec8-2762a9eee6b0",
            key: "node_input",
            value: {
              rules: [],
              combinator: "OR",
            },
          },
        ],
        trigger: {
          id: "2892f5b0-a6c9-4854-ac53-cf5e17b9ae16",
          merge_behavior: "AWAIT_ANY",
        },
        outputs: [
          {
            id: "cff5b127-113b-42ed-aa08-d300ac3583c1",
            name: "value",
            type: "DOCUMENT",
            value: {
              type: "NODE_OUTPUT",
              node_id: "a1bd3a26-21b8-44e8-8c1c-213cb5f7d5e2",
              node_output_id: "3728d2d3-e38c-4d5c-a02e-05853f71ef2a",
            },
            schema: {
              type: "string",
            },
          },
        ],
      },
      {
        id: "a1bd3a26-21b8-44e8-8c1c-213cb5f7d5e2",
        type: "TEMPLATING",
        data: {
          output_id: "3728d2d3-e38c-4d5c-a02e-05853f71ef2a",
          error_output_id: null,
          label: "Templating",
          source_handle_id: "c329bedf-030b-4654-a185-12ce657240ff",
          target_handle_id: "3d66d0dd-45f6-4098-a534-f84ea600e1c9",
          template_node_input_id: "31eab6ad-f3a3-4abc-acc1-2f50fe970a3b",
          output_type: "STRING",
        },
        inputs: [
          {
            id: "31eab6ad-f3a3-4abc-acc1-2f50fe970a3b",
            key: "template",
            value: {
              rules: [],
              combinator: "OR",
            },
          },
        ],
        trigger: {
          id: "3d66d0dd-45f6-4098-a534-f84ea600e1c9",
          merge_behavior: "AWAIT_ATTRIBUTES",
        },
        ports: [
          {
            id: "c329bedf-030b-4654-a185-12ce657240ff",
            type: "DEFAULT",
            name: "default",
          },
        ],
        adornments: null,
      },
    ],
    edges: [
      {
        id: "5a9b5158-67e1-4dd1-bea0-2d48bd10fa22",
        type: "DEFAULT",
        source_node_id: "7be676ae-b011-454b-aa59-0c26385a543c",
        source_handle_id: "3006c2ba-2638-4494-9154-9a716ab2af63",
        target_node_id: "a1bd3a26-21b8-44e8-8c1c-213cb5f7d5e2",
        target_handle_id: "3d66d0dd-45f6-4098-a534-f84ea600e1c9",
      },
      {
        id: "6b92f989-825a-44f8-8c0e-22151749f0d7",
        type: "DEFAULT",
        source_node_id: "a1bd3a26-21b8-44e8-8c1c-213cb5f7d5e2",
        source_handle_id: "c329bedf-030b-4654-a185-12ce657240ff",
        target_node_id: "b1ede5dd-2c27-442f-bf59-77a87caf2184",
        target_handle_id: "2892f5b0-a6c9-4854-ac53-cf5e17b9ae16",
      },
    ],
    output_values: [
      {
        output_variable_id: "cff5b127-113b-42ed-aa08-d300ac3583c1",
        value: {
          type: "NODE_OUTPUT",
          node_id: "b1ede5dd-2c27-442f-bf59-77a87caf2184",
          node_output_id: "cff5b127-113b-42ed-aa08-d300ac3583c1",
        },
      },
    ],
  },
  dataset: [
    {
      id: "3ef81970-e156-426a-ad01-84a8d9de9ce6",
      label: "Scenario 1",
      inputs: [
        {
          name: "document",
          type: "DOCUMENT",
          value: null,
        },
      ],
      mocks: [],
      workflow_trigger_id: null,
    },
  ],
  input_variables: [
    {
      id: "3757936a-81e2-4c4c-be2b-86497b25f411",
      key: "document",
      type: "DOCUMENT",
      required: false,
      default: {
        type: "DOCUMENT",
        value: null,
      },
      extensions: {
        color: "deepPurple",
        description: null,
        title: null,
      },
      schema: null,
    },
  ],
  output_variables: [
    {
      id: "cff5b127-113b-42ed-aa08-d300ac3583c1",
      key: "final-output",
      type: "DOCUMENT",
      required: null,
      default: null,
      extensions: null,
      schema: null,
    },
  ],
  state_variables: [],
  triggers: [],
  assertions: ["sandbox.py"],
};
