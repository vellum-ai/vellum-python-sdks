import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { nodeAttributeFactory } from "src/__test__/helpers/node-attribute-factory";
import {
  nodePortFactory,
  toolCallingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { Writer } from "src/generators/extensions/writer";
import { GenericNode } from "src/generators/nodes/generic-node";
import {
  FunctionArgs,
  MCPServerFunctionArgs,
  NodePort,
  WorkflowDeploymentFunctionArgs,
} from "src/types/vellum";

describe("ToolCallingNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: GenericNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory({ strict: false });
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "input-1",
          key: "location",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "2544f9e4-d6e6-4475-b6a9-13393115d77c",
        }),
      ];
      const nodeData = toolCallingNodeFactory({ nodePorts: nodePortData });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("input variables", () => {
    it("should generate input variables", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [
          {
            id: "b5ae358b-e111-4209-9a3e-4e7126f2d391",
            name: "ml_model",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "gpt-4o-mini" },
            },
          },
          {
            id: "be73bec8-a35a-43b1-b140-9541ba837f8e",
            name: "prompt_inputs",
            value: {
              type: "DICTIONARY_REFERENCE",
              entries: [
                {
                  id: "1dc7d5dc-c41d-4a9b-8add-1e0c6705da04",
                  key: "text",
                  value: null,
                },
              ],
            },
          },
          {
            id: "dfdafe9a-1dae-4895-8a08-22b71c0119ff",
            name: "blocks",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: [
                  {
                    blocks: [
                      {
                        blocks: [
                          {
                            text: "Summarize the following text:\n\n",
                            block_type: "PLAIN_TEXT",
                          },
                          {
                            block_type: "VARIABLE",
                            input_variable:
                              "1dc7d5dc-c41d-4a9b-8add-1e0c6705da04",
                          },
                        ],
                        block_type: "RICH_TEXT",
                      },
                    ],
                    chat_role: "SYSTEM",
                    block_type: "CHAT_MESSAGE",
                  },
                ],
              },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("composio tool", () => {
    it.each([
      {
        name: "with integration_name and tool_slug",
        composioToolFunction: {
          type: "COMPOSIO",
          name: "github_create_an_issue",
          integration_name: "GITHUB", // legacy field, use toolkit
          tool_slug: "GITHUB_CREATE_AN_ISSUE", // legacy field, use action
          description: "Create a new issue in a GitHub repository",
        },
      },
      {
        name: "with toolkit and action",
        composioToolFunction: {
          type: "COMPOSIO",
          name: "github_create_an_issue",
          toolkit: "GITHUB",
          action: "GITHUB_CREATE_AN_ISSUE",
          description: "Create a new issue in a GitHub repository",
        },
      },
    ])(
      "should generate composio tool $name",
      async ({ composioToolFunction }) => {
        const nodePortData: NodePort[] = [
          nodePortFactory({
            id: "port-id",
          }),
        ];

        const functionsAttribute = nodeAttributeFactory(
          "functions-attr-id",
          "functions",
          {
            type: "CONSTANT_VALUE",
            value: {
              type: "JSON",
              value: [composioToolFunction],
            },
          }
        );

        const nodeData = toolCallingNodeFactory({
          nodePorts: nodePortData,
          nodeAttributes: [functionsAttribute],
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as GenericNodeContext;

        const node = new GenericNode({
          workflowContext,
          nodeContext,
        });

        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      }
    );

    // TODO: Combine this with the test above once attributes are finalized
    // This test was written to repro a codegen bug that is now fixed
    it("should handle composio tool with integration_name & tool_slug fields", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const composioToolFunction = {
        type: "COMPOSIO",
        name: "GMAIL_CREATE_EMAIL_DRAFT",
        tool_name: "Create email draft",
        tool_slug: "GMAIL_CREATE_EMAIL_DRAFT",
        description:
          "Creates a gmail email draft, supporting to/cc/bcc, subject, plain/html body (ensure `is html=true` for html), attachments, and threading.",
        connection_id: "ca_QoaKIKPlluHk",
        integration_name: "gmail",
      };

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [composioToolFunction],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      // This should not throw a TypeError
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("function ordering", () => {
    const codeExecutionFunction: FunctionArgs = {
      type: "CODE_EXECUTION",
      src: 'def add_numbers(a: int, b: int) -> int:\n    """\n    Add two numbers together.\n    """\n    return a + b\n',
      name: "add_numbers",
      description: "Add two numbers together.",
      definition: {
        name: "add_numbers",
        parameters: {
          type: "object",
          required: ["a", "b"],
          properties: {
            a: { type: "integer" },
            b: { type: "integer" },
          },
        },
      },
    };

    const inlineWorkflowFunction = {
      type: "INLINE_WORKFLOW",
      exec_config: {
        workflow_raw_data: {
          nodes: [
            {
              id: "entrypoint",
              type: "ENTRYPOINT",
              data: {
                label: "Entrypoint Node",
                source_handle_id: "entry-source",
              },
              inputs: [],
            },
            {
              id: "subtract-node",
              type: "GENERIC",
              label: "SubtractNode",
              base: {
                name: "BaseNode",
                module: ["vellum", "workflows", "nodes", "bases", "base"],
              },
              attributes: [],
              outputs: [
                {
                  id: "subtract-output",
                  name: "result",
                  type: "NUMBER",
                },
              ],
              ports: [],
              trigger: {
                id: "subtract-trigger",
                merge_behavior: "AWAIT_ATTRIBUTES",
              },
            },
          ],
          edges: [
            {
              id: "edge-1",
              type: "DEFAULT",
              source_node_id: "entrypoint",
              source_handle_id: "entry-source",
              target_node_id: "subtract-node",
              target_handle_id: "subtract-trigger",
            },
          ],
          definition: {
            name: "SubtractWorkflow",
            module: ["workflows", "subtract"],
          },
        },
        input_variables: [
          {
            id: "input-a",
            key: "a",
            type: "NUMBER",
            default: null,
            required: true,
            extensions: { color: null },
          },
          {
            id: "input-b",
            key: "b",
            type: "NUMBER",
            default: null,
            required: true,
            extensions: { color: null },
          },
        ],
        output_variables: [
          {
            id: "output-result",
            key: "result",
            type: "NUMBER",
          },
        ],
      },
    };

    it("should preserve order: code-exec, workflow", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [codeExecutionFunction, inlineWorkflowFunction],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should preserve order: workflow, code-exec", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [inlineWorkflowFunction, codeExecutionFunction],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
  describe("inline workflow", () => {
    it("should generate inline workflow function name", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functions = {
        name: "subtract",
        type: "INLINE_WORKFLOW",
        description: "subtract two numbers",
        exec_config: {
          runner_config: {},
          input_variables: [],
          state_variables: [],
          output_variables: [],
          workflow_raw_data: {
            edges: [],
            nodes: [],
            definition: null, // Testing null definition
            output_values: [],
          },
        },
      };

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [functions],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("workflow deployment", () => {
    const deploymentWorkflowFunction: WorkflowDeploymentFunctionArgs = {
      type: "WORKFLOW_DEPLOYMENT",
      name: "deployment_1",
      description: "Deployment 1 description",
      deployment: "deployment_1",
      release_tag: null,
    };

    it("should generate latest release tag if release_tag is null", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [deploymentWorkflowFunction],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
  describe("mcp server", () => {
    const mcpServerFunction: MCPServerFunctionArgs = {
      type: "MCP_SERVER",
      name: "github",
      url: "https://api.githubcopilot.com/mcp/",
      authorization_type: "BEARER_TOKEN",
      bearer_token_value: "GITHUB_PERSONAL_ACCESS_TOKEN",
      api_key_header_key: null,
      api_key_header_value: null,
    };

    it("should generate mcp server", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [mcpServerFunction],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it("should generate mcp server with no authorization type", async () => {
      const mcpServerFunction: MCPServerFunctionArgs = {
        type: "MCP_SERVER",
        name: "github",
        url: "https://api.githubcopilot.com/mcp/",
        bearer_token_value: null,
        api_key_header_key: null,
        api_key_header_value: null,
      };
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [mcpServerFunction],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it("should generate mcp server with null authorization type", async () => {
      const mcpServerFunction: MCPServerFunctionArgs = {
        type: "MCP_SERVER",
        name: "github",
        url: "https://api.githubcopilot.com/mcp/",
        authorization_type: null,
        bearer_token_value: null,
        api_key_header_key: null,
        api_key_header_value: null,
      };
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [mcpServerFunction],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("no tools with jinja blocks", () => {
    it("should be resilient to extra keys in jinja blocks", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const blocksAttribute = nodeAttributeFactory("blocks-attr-id", "blocks", {
        type: "CONSTANT_VALUE",
        value: {
          type: "JSON",
          value: [
            {
              block_type: "JINJA",
              template: "Hello world",
              blocks: [],
            },
          ],
        },
      });

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [blocksAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle invalid jinja blocks with missing template field", async () => {
      /**
       * Tests that invalid blocks with missing template field are handled gracefully
       * by adding errors to workflow context while preserving valid blocks.
       */

      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const blocksAttribute = nodeAttributeFactory("blocks-attr-id", "blocks", {
        type: "CONSTANT_VALUE",
        value: {
          type: "JSON",
          value: [
            {
              block_type: "JINJA",
              blocks: [],
            },
            {
              block_type: "JINJA",
              template: "Valid template",
              blocks: [],
            },
          ],
        },
      });

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [blocksAttribute],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(workflowContext.getErrors()).toHaveLength(1);
      expect(workflowContext.getErrors()[0]?.message).toContain(
        "Failed to parse block"
      );
    });
  });

  describe("function name casing", () => {
    const testCases = [["parseJSON"], ["123invalid"], ["special-chars!"]];

    it.each(testCases)("preserves casing: %s", async (name) => {
      const functions = [
        { type: "CODE_EXECUTION", name, src: `def ${name}(): pass` },
      ];

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: { type: "JSON", value: functions },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: [nodePortFactory({ id: "port-id" })],
        nodeAttributes: [functionsAttribute],
        label: "CasingTestNode",
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;
      const node = new GenericNode({ workflowContext, nodeContext });

      node.getNodeFile().write(writer);
      const output = await writer.toStringFormatted();

      expect(output).toMatchSnapshot();
    });
  });

  describe("parent input references", () => {
    it.skip("should handle tool calling node with parent input references in function inputs", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "c67bc06f-3a69-42a1-8e34-d45a11754871",
        }),
      ];

      const nodeData = toolCallingNodeFactory({
        id: "6a87bc82-4371-44ae-b9d9-89e891817be2",
        label: "String Tool Calling Node",
        nodePorts: nodePortData,
        nodeAttributes: [
          {
            id: "130f538a-d544-48a8-bb7f-a0da78e90775",
            name: "ml_model",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "gpt-4o-mini" },
            },
          },
          {
            id: "261a517e-3874-483b-b497-4139bbee34fc",
            name: "blocks",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: [
                  {
                    block_type: "CHAT_MESSAGE",
                    state: null,
                    cache_config: null,
                    chat_role: "SYSTEM",
                    chat_source: null,
                    chat_message_unterminated: null,
                    blocks: [
                      {
                        block_type: "RICH_TEXT",
                        state: null,
                        cache_config: null,
                        blocks: [
                          {
                            block_type: "PLAIN_TEXT",
                            state: null,
                            cache_config: null,
                            text: "You are a string expert. Use the provided parent input.",
                          },
                        ],
                      },
                    ],
                  },
                  {
                    block_type: "CHAT_MESSAGE",
                    state: null,
                    cache_config: null,
                    chat_role: "USER",
                    chat_source: null,
                    chat_message_unterminated: null,
                    blocks: [
                      {
                        block_type: "RICH_TEXT",
                        state: null,
                        cache_config: null,
                        blocks: [
                          {
                            block_type: "VARIABLE",
                            state: null,
                            cache_config: null,
                            input_variable:
                              "026ff7aa-0aa0-4980-bde0-8d16e6744d2d",
                          },
                        ],
                      },
                    ],
                  },
                ],
              },
            },
          },
          {
            id: "e2695720-919b-497e-8d01-ae6aa705f7bb",
            name: "functions",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: [
                  {
                    type: "CODE_EXECUTION",
                    name: "get_string",
                    description:
                      "\n    Get a string with the parent input, dummy input, and the populated input.\n    ",
                    definition: {
                      state: null,
                      cache_config: null,
                      name: "get_string",
                      description:
                        "\n    Get a string with the parent input, dummy input, and the populated input.\n    ",
                      parameters: {
                        type: "object",
                        properties: { populated_input: { type: "string" } },
                        required: ["populated_input"],
                      },
                      inputs: {
                        type: "DICTIONARY_REFERENCE",
                        entries: [
                          {
                            id: "11c6f6ee-6b1e-4070-90d6-05293d4da7fd",
                            key: "parent_input",
                            value: {
                              type: "WORKFLOW_INPUT",
                              input_variable_id:
                                "4bf1f0e7-76c6-4204-9f8c-bd9c3b73a8db",
                            },
                          },
                          {
                            id: "0b86e78e-f3ec-44dd-9969-9a7c0bd634fc",
                            key: "dummy_input",
                            value: {
                              type: "NODE_OUTPUT",
                              node_id: "72f78142-e0a2-40a9-ae70-0230ccf3b503",
                              node_output_id:
                                "6e639661-d0dc-4586-9393-e64e95e0d3ef",
                            },
                          },
                          {
                            id: "31856421-ac85-47bc-bac8-923a3fba351e",
                            key: "constant_input",
                            value: {
                              type: "CONSTANT_VALUE",
                              value: {
                                type: "STRING",
                                value: "constant_input",
                              },
                            },
                          },
                        ],
                      },
                      forced: null,
                      strict: null,
                    },
                    src: 'from .inputs import ParentInputs\nfrom .nodes.dummy_node import DummyNode\n\ndef get_string(parent_input: str, dummy_input: str, constant_input: str, populated_input: str) -> str:\n    """\n    Get a string with the parent input, dummy input, and the populated input.\n    """\n    return f\'parent input: {parent_input}, dummy input: {dummy_input}, constant input: {constant_input}, populated input: {populated_input}\'\n',
                  },
                ],
              },
            },
          },
          {
            id: "51d32393-131a-4862-8ffc-c7ae03eacdc5",
            name: "prompt_inputs",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: { question: "What's the string like?" },
              },
            },
          },
          {
            id: "e7229551-851f-489f-8c45-ffe737d51aee",
            name: "parameters",
            value: {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: {
                  stop: [],
                  temperature: 0.0,
                  max_tokens: 4096.0,
                  top_p: 1.0,
                  top_k: 0.0,
                  frequency_penalty: 0.0,
                  presence_penalty: 0.0,
                  logit_bias: null,
                  custom_parameters: null,
                },
              },
            },
          },
          {
            id: "6da59924-9a30-44bd-aad4-2cd7ce33fc8a",
            name: "max_prompt_iterations",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "NUMBER", value: 25.0 },
            },
          },
          {
            id: "481c4067-1c32-4a1b-a643-0dd42d8d46fc",
            name: "settings",
            value: {
              type: "CONSTANT_VALUE",
              value: { type: "JSON", value: null },
            },
          },
        ],
        nodeOutputs: [
          {
            id: "dafaab89-e5a4-46cd-b850-22f5624f4697",
            name: "text",
            type: "STRING",
          },
          {
            id: "588a6994-64e3-4538-9642-30b8fab70d55",
            name: "chat_history",
            type: "CHAT_HISTORY",
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
