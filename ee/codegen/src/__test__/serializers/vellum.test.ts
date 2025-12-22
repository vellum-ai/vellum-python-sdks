import { WorkflowNodeSerializer } from "src/serializers/vellum";

describe("vellum", () => {
  describe("PromptNodeSerializer", () => {
    it("should serialize legacy prompt nodes", () => {
      const data = {
        id: "aa81d132-9e77-4278-97c9-620dd66bec6d",
        type: "PROMPT",
        data: {
          variant: "LEGACY",
          label: "Prompt Node",
          output_id: "14beb2dd-603b-4f0b-9d03-3a72c5116c0b",
          array_output_id: "b8918533-c202-45be-9e2b-a84e428a0ea7",
          error_output_id: "273c6835-1335-40aa-93b4-edd9752983a1",
          source_handle_id: "78b60703-b52d-47f3-b534-bd349502686e",
          target_handle_id: "0305a081-3cf8-47b4-930f-c00950b853b4",
          sandbox_routing_config: {
            version: 2,
            prompt_version_data: {
              ml_model_to_workspace_id: "d883c492-d9f4-469f-9809-009c12b11325",
              exec_config: {
                parameters: {
                  stop: null,
                  temperature: 0,
                  max_tokens: 1198,
                  top_p: 1,
                  top_k: 0,
                  frequency_penalty: 0,
                  presence_penalty: 0,
                  logit_bias: {},
                  custom_parameters: null,
                },
                input_variables: [
                  {
                    id: "ac96a699-ef55-4814-bc37-b4298abcb08b",
                    key: "question",
                    type: "STRING",
                    required: null,
                    default: null,
                    extensions: null,
                  },
                  {
                    id: "77f9a566-88f6-442b-92c1-21132b9605c5",
                    key: "context",
                    type: "STRING",
                    required: null,
                    default: null,
                    extensions: null,
                  },
                  {
                    id: "2560fb85-a3c0-4c54-9060-b0bdd2613d2f",
                    key: "$chat_history",
                    type: "CHAT_HISTORY",
                    required: null,
                    default: null,
                    extensions: null,
                  },
                ],
                prompt_template_block_data: {
                  blocks: [
                    {
                      block_type: "CHAT_MESSAGE",
                      properties: {
                        blocks: [
                          {
                            block_type: "JINJA",
                            properties: {
                              template:
                                "Answer the question given the policy quotes. Provide citation of the policy you got it from at the end of the response. You should strictly only draw upon information from the provided context above. If you're unable to answer the question using the policy quotes, say \"Sorry, I don't know\"",
                              template_type: "STRING",
                            },
                            id: "f54c32f7-1481-4fce-a1a4-9fe9423aa0fc",
                            state: "ENABLED",
                            cache_config: null,
                          },
                          {
                            block_type: "RICH_TEXT",
                            blocks: [
                              {
                                block_type: "PLAIN_TEXT",
                                text: "Question:\n---------------\n",
                                id: "d5af0081-9e73-4c49-a02c-1f359142af90",
                                state: "ENABLED",
                                cache_config: null,
                              },
                              {
                                block_type: "VARIABLE",
                                id: "7fe66db4-b059-4c59-97fb-e6a15c728506",
                                state: "ENABLED",
                                cache_config: null,
                                input_variable_id:
                                  "ac96a699-ef55-4814-bc37-b4298abcb08b",
                              },
                              {
                                block_type: "PLAIN_TEXT",
                                text: "\n\nPolicy Quotes:\n-----------------------\n",
                                id: "c44ba208-e424-4fe6-94a3-7329af14b8c1",
                                state: "ENABLED",
                                cache_config: null,
                              },
                              {
                                block_type: "VARIABLE",
                                id: "8bda4e49-cfaa-43d4-a6da-991c839b6566",
                                state: "ENABLED",
                                cache_config: null,
                                input_variable_id:
                                  "77f9a566-88f6-442b-92c1-21132b9605c5",
                              },
                            ],
                            id: "bab4d2b4-7ebf-4236-9fda-02e0285c6579",
                            state: "ENABLED",
                            cache_config: null,
                          },
                          {
                            block_type: "JINJA",
                            properties: {
                              template: "Limit your response to 100 words.",
                              template_type: "STRING",
                            },
                            id: "f18a710f-15e4-4d3c-b0c9-4737494d4952",
                            state: "ENABLED",
                            cache_config: null,
                          },
                        ],
                        chat_role: "SYSTEM",
                        chat_source: null,
                        chat_message_unterminated: false,
                      },
                      id: "e00f1f5f-6499-4ec9-8056-d0d80af4f12a",
                      state: "ENABLED",
                      cache_config: null,
                    },
                  ],
                  version: 1,
                },
                settings: null,
              },
            },
          },
          source_sandbox: null,
          deployment: {
            deployment_id: "4477ce94-068c-443f-b2bb-1fb763bdfdb9",
            deployment_release_tag_id: "5859bea5-640e-4d4b-bd93-374fa5d67a94",
          },
        },
        inputs: [
          {
            id: "ac96a699-ef55-4814-bc37-b4298abcb08b",
            key: "question",
            value: {
              rules: [
                {
                  type: "NODE_OUTPUT",
                  data: {
                    node_id: "4e875992-8e13-4df4-9c44-7facd37743ed",
                    output_id: "5126839b-cc66-4043-9572-711eec42d396",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "77f9a566-88f6-442b-92c1-21132b9605c5",
            key: "context",
            value: {
              rules: [
                {
                  type: "NODE_OUTPUT",
                  data: {
                    node_id: "9f071343-91e8-4932-b4b3-cd8be2d7b291",
                    output_id: "f1af14ab-cb12-44f5-8cef-6da9b8932077",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "2560fb85-a3c0-4c54-9060-b0bdd2613d2f",
            key: "$chat_history",
            value: {
              rules: [
                {
                  type: "INPUT_VARIABLE",
                  data: {
                    input_variable_id: "d359379f-944f-4631-b4c8-2c6811cef063",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
        display_data: {
          width: 480,
          height: 278,
          position: {
            x: 1124.121795913808,
            y: 22.929068704919985,
          },
        },
        definition: null,
      };

      const parsedData = WorkflowNodeSerializer.parse(data);
      expect(parsedData.ok).toBe(true);
    });
  });
});
