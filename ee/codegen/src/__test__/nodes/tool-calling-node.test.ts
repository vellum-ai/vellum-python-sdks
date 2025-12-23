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

  describe("vellum integration tool", () => {
    it("should generate vellum integration tool with toolkit_version", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const vellumIntegrationToolFunction = {
        type: "VELLUM_INTEGRATION",
        provider: "COMPOSIO",
        integration_name: "GITHUB",
        name: "github_create_issue",
        description: "Create a new issue in a GitHub repository",
        toolkit_version: "1.2.3",
      };

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [vellumIntegrationToolFunction],
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

    it("should generate vellum integration tool without toolkit_version", async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      const vellumIntegrationToolFunction = {
        type: "VELLUM_INTEGRATION",
        provider: "COMPOSIO",
        integration_name: "SLACK",
        name: "slack_send_message",
        description: "Send a message to a Slack channel",
      };

      const functionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "JSON",
            value: [vellumIntegrationToolFunction],
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

    it("should generate mcp server with ARRAY_REFERENCE format and EnvironmentVariableReference", async () => {
      /**
       * Tests that MCPServer with EnvironmentVariableReference serialized as
       * ARRAY_REFERENCE+DICTIONARY_REFERENCE generates correct code.
       * This is the new serialization format used when MCPServer contains dynamic references.
       *
       * Note: The only difference between this and the legacy CONSTANT_VALUE format is that
       * authorization_type is generated as a string (e.g., "API_KEY") instead of an enum
       * (e.g., AuthorizationType.API_KEY). Both are functionally equivalent since Pydantic
       * coerces the string to the enum at runtime.
       */

      // GIVEN the new ARRAY_REFERENCE+DICTIONARY_REFERENCE representation
      const arrayReferenceFunctionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "ARRAY_REFERENCE",
          items: [
            {
              type: "DICTIONARY_REFERENCE",
              entries: [
                {
                  key: "name",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "my-mcp-server" },
                  },
                },
                {
                  key: "url",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "STRING",
                      value: "https://my-mcp-server.com",
                    },
                  },
                },
                {
                  key: "authorization_type",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "API_KEY" },
                  },
                },
                {
                  key: "api_key_header_key",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "my-api-key-header-key" },
                  },
                },
                {
                  key: "api_key_header_value",
                  value: {
                    type: "ENVIRONMENT_VARIABLE",
                    environmentVariable: "my-api-key-header-value",
                  },
                },
              ],
              definition: {
                name: "MCPServer",
                module: ["vellum", "workflows", "types", "definition"],
              },
            },
          ],
        }
      );

      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      // WHEN we generate code for the new ARRAY_REFERENCE format
      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [arrayReferenceFunctionsAttribute],
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
      const code = await writer.toStringFormatted();

      // THEN the generated code should contain the MCPServer with EnvironmentVariableReference
      expect(code).toContain("MCPServer(");
      expect(code).toContain('name="my-mcp-server"');
      expect(code).toContain('url="https://my-mcp-server.com"');
      expect(code).toContain('api_key_header_key="my-api-key-header-key"');
      expect(code).toContain("EnvironmentVariableReference(");
      expect(code).toContain('name="my-api-key-header-value"');

      // AND the full output should match the snapshot
      expect(code).toMatchSnapshot();
    });

    it("should generate mixed functions with all supported function types in ARRAY_REFERENCE format", async () => {
      /**
       * Tests that a ToolCallingNode with all supported function types in ARRAY_REFERENCE format
       * generates correct code. This includes:
       * - CODE_EXECUTION function (serialized as CONSTANT_VALUE)
       * - MCP_SERVER with EnvironmentVariableReference (serialized as DICTIONARY_REFERENCE)
       * - INLINE_WORKFLOW (serialized as CONSTANT_VALUE)
       * - COMPOSIO (serialized as CONSTANT_VALUE)
       * - VELLUM_INTEGRATION (serialized as CONSTANT_VALUE)
       * - WORKFLOW_DEPLOYMENT (serialized as CONSTANT_VALUE)
       */

      const arrayReferenceFunctionsAttribute = nodeAttributeFactory(
        "functions-attr-id",
        "functions",
        {
          type: "ARRAY_REFERENCE",
          items: [
            {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: {
                  src: 'def add(a: int, b: int):\n    """Description of function_1"""\n    return a + b',
                  name: "add",
                  type: "CODE_EXECUTION",
                  definition: {
                    name: "add",
                    state: null,
                    forced: null,
                    inputs: null,
                    strict: null,
                    parameters: {
                      type: "object",
                      required: ["a", "b"],
                      properties: {
                        a: { type: "integer" },
                        b: { type: "integer" },
                      },
                    },
                    description: "Description of function_1",
                    cache_config: null,
                  },
                  description: "Description of function_1",
                },
              },
            },
            {
              type: "DICTIONARY_REFERENCE",
              entries: [
                {
                  id: "41a085ca-d80d-4f77-9d94-dd2045251c49",
                  key: "type",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "MCP_SERVER" },
                  },
                },
                {
                  id: "44a97bcf-5c73-4ee7-abc9-03f2704f4657",
                  key: "name",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "github" },
                  },
                },
                {
                  id: "f595fcea-5295-4822-881f-7054652b6ac2",
                  key: "description",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "" },
                  },
                },
                {
                  id: "147ae38b-56f7-452a-93d4-6291ce9fa26f",
                  key: "url",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "STRING",
                      value: "https://api.githubcopilot.com/mcp/",
                    },
                  },
                },
                {
                  id: "297bd5da-9385-4058-be68-f7987c2f2ad0",
                  key: "authorization_type",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "API_KEY" },
                  },
                },
                {
                  id: "727f5be2-d55f-4039-a42f-f8c9783804bd",
                  key: "bearer_token_value",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "JSON", value: null },
                  },
                },
                {
                  id: "1c5f7c73-e416-4256-be90-f216ff7ed8f4",
                  key: "api_key_header_key",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "aaa" },
                  },
                },
                {
                  id: "da14526d-a337-4ca3-82b0-b681cce999c6",
                  key: "api_key_header_value",
                  value: {
                    type: "ENVIRONMENT_VARIABLE",
                    environmentVariable: "FIRECRAWL",
                  },
                },
              ],
              definition: {
                name: "MCPServer",
                module: ["vellum", "workflows", "types", "definition"],
              },
            },
            {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: {
                  name: "Subtract",
                  type: "INLINE_WORKFLOW",
                  description: "",
                  exec_config: {
                    input_variables: [
                      {
                        id: "578081cf-490e-47c8-9335-d3e88e7c8a9f",
                        key: "var_1",
                        type: "NUMBER",
                        default: null,
                        required: false,
                        extensions: { color: "teal" },
                      },
                      {
                        id: "1b13dc78-45d7-4bdc-8df5-64e4a7e63d0b",
                        key: "var_2",
                        type: "NUMBER",
                        default: null,
                        required: false,
                        extensions: { color: "peach" },
                      },
                    ],
                    state_variables: [],
                    output_variables: [
                      {
                        id: "29b899b0-6e71-4e21-aaf2-5da484f9d088",
                        key: "output",
                        type: "NUMBER",
                      },
                    ],
                    workflow_raw_data: {
                      edges: [
                        {
                          id: "2cdc8ebb-a01e-4cf8-bf22-14b2e90ee42b",
                          type: "DEFAULT",
                          source_node_id:
                            "45fae5fa-553e-432c-bf9e-d22b669dc5d5",
                          target_node_id:
                            "6aa59f91-6d5d-4f11-97cf-bdab0773972b",
                          source_handle_id:
                            "bb2cfe41-f0d1-4375-b4d8-e415df678808",
                          target_handle_id:
                            "1d5cea3d-9686-4903-a2b1-420e3c63934c",
                        },
                        {
                          id: "de27a328-463e-4d84-bf13-eb267d1a339f",
                          type: "DEFAULT",
                          display_data: { z_index: 0 },
                          source_node_id:
                            "6aa59f91-6d5d-4f11-97cf-bdab0773972b",
                          target_node_id:
                            "d3d58aa4-ae05-4fc9-ba77-315cac5f4f06",
                          source_handle_id:
                            "ff54ed7c-06ec-46cc-8e51-71e92c06c408",
                          target_handle_id:
                            "24d76ce4-c2b4-4988-88f8-f59ab3f09a34",
                        },
                      ],
                      nodes: [
                        {
                          id: "45fae5fa-553e-432c-bf9e-d22b669dc5d5",
                          base: null,
                          data: {
                            label: "Entrypoint Node",
                            source_handle_id:
                              "bb2cfe41-f0d1-4375-b4d8-e415df678808",
                          },
                          type: "ENTRYPOINT",
                          inputs: [],
                          definition: null,
                          display_data: {
                            icon: "vellum:icon:play",
                            color: "default",
                            width: 306,
                            height: 88,
                            z_index: 2,
                            position: { x: 1545.0, y: 330.0 },
                          },
                        },
                        {
                          id: "6aa59f91-6d5d-4f11-97cf-bdab0773972b",
                          base: {
                            name: "CodeExecutionNode",
                            module: [
                              "vellum",
                              "workflows",
                              "nodes",
                              "displayable",
                              "code_execution_node",
                              "node",
                            ],
                          },
                          data: {
                            label: "Code Execution",
                            packages: [],
                            output_id: "32b2f0d3-fc4b-4e0c-997b-690de7de0912",
                            output_type: "JSON",
                            code_input_id:
                              "446b935c-3840-472d-bab9-f232cb7f997f",
                            log_output_id:
                              "3f9245fe-7c3f-4c20-b737-472d857a2aaa",
                            error_output_id: null,
                            runtime_input_id:
                              "05ae0ae1-0c18-42a3-9ce8-03c60dccfc91",
                            source_handle_id:
                              "ff54ed7c-06ec-46cc-8e51-71e92c06c408",
                            target_handle_id:
                              "1d5cea3d-9686-4903-a2b1-420e3c63934c",
                          },
                          type: "CODE_EXECUTION",
                          ports: [
                            {
                              id: "ff54ed7c-06ec-46cc-8e51-71e92c06c408",
                              name: "default",
                              type: "DEFAULT",
                            },
                          ],
                          inputs: [
                            {
                              id: "da5e7929-57f0-48af-96f3-d71ad6d71985",
                              key: "var_1",
                              value: {
                                rules: [
                                  {
                                    data: {
                                      input_variable_id:
                                        "578081cf-490e-47c8-9335-d3e88e7c8a9f",
                                    },
                                    type: "INPUT_VARIABLE",
                                  },
                                ],
                                combinator: "OR",
                              },
                            },
                            {
                              id: "ebc1e6aa-f856-4e00-8686-b302ce85edc4",
                              key: "var_2",
                              value: {
                                rules: [
                                  {
                                    data: {
                                      input_variable_id:
                                        "1b13dc78-45d7-4bdc-8df5-64e4a7e63d0b",
                                    },
                                    type: "INPUT_VARIABLE",
                                  },
                                ],
                                combinator: "OR",
                              },
                            },
                            {
                              id: "446b935c-3840-472d-bab9-f232cb7f997f",
                              key: "code",
                              value: {
                                rules: [
                                  {
                                    data: {
                                      type: "STRING",
                                      value:
                                        '"""\nYou must define a function called `main` whose arguments are named after the\nInput Variables.\n"""\n\ndef main(var_1: int, var_2: int) -> int:\n    return var_1 - var_2\n',
                                    },
                                    type: "CONSTANT_VALUE",
                                  },
                                ],
                                combinator: "OR",
                              },
                            },
                            {
                              id: "05ae0ae1-0c18-42a3-9ce8-03c60dccfc91",
                              key: "runtime",
                              value: {
                                rules: [
                                  {
                                    data: {
                                      type: "STRING",
                                      value: "PYTHON_3_11_6",
                                    },
                                    type: "CONSTANT_VALUE",
                                  },
                                ],
                                combinator: "OR",
                              },
                            },
                          ],
                          outputs: [
                            {
                              id: "32b2f0d3-fc4b-4e0c-997b-690de7de0912",
                              name: "result",
                              type: "NUMBER",
                              value: null,
                              schema: {
                                anyOf: [
                                  { type: "number" },
                                  { type: "integer" },
                                ],
                              },
                            },
                            {
                              id: "3f9245fe-7c3f-4c20-b737-472d857a2aaa",
                              name: "log",
                              type: "STRING",
                              value: null,
                              schema: { type: "string" },
                            },
                          ],
                          trigger: {
                            id: "1d5cea3d-9686-4903-a2b1-420e3c63934c",
                            merge_behavior: "AWAIT_ATTRIBUTES",
                          },
                          definition: {
                            name: "CodeExecution",
                            module: [
                              "new_workflow",
                              "nodes",
                              "agent",
                              "subtract",
                              "nodes",
                              "code_execution",
                            ],
                          },
                          display_data: {
                            width: 370,
                            height: 92,
                            z_index: 4,
                            position: {
                              x: 2045.8736080178173,
                              y: 314.98374860801783,
                            },
                          },
                        },
                        {
                          id: "d3d58aa4-ae05-4fc9-ba77-315cac5f4f06",
                          base: {
                            name: "FinalOutputNode",
                            module: [
                              "vellum",
                              "workflows",
                              "nodes",
                              "displayable",
                              "final_output_node",
                              "node",
                            ],
                          },
                          data: {
                            name: "output",
                            label: "Output",
                            output_id: "29b899b0-6e71-4e21-aaf2-5da484f9d088",
                            output_type: "NUMBER",
                            node_input_id:
                              "42549c0a-60cb-4a7a-a830-68f022c02e03",
                            target_handle_id:
                              "24d76ce4-c2b4-4988-88f8-f59ab3f09a34",
                          },
                          type: "TERMINAL",
                          ports: [],
                          inputs: [
                            {
                              id: "42549c0a-60cb-4a7a-a830-68f022c02e03",
                              key: "node_input",
                              value: {
                                rules: [
                                  {
                                    data: {
                                      node_id:
                                        "6aa59f91-6d5d-4f11-97cf-bdab0773972b",
                                      output_id:
                                        "32b2f0d3-fc4b-4e0c-997b-690de7de0912",
                                    },
                                    type: "NODE_OUTPUT",
                                  },
                                ],
                                combinator: "OR",
                              },
                            },
                          ],
                          outputs: [
                            {
                              id: "29b899b0-6e71-4e21-aaf2-5da484f9d088",
                              name: "value",
                              type: "NUMBER",
                              value: {
                                type: "NODE_OUTPUT",
                                node_id: "6aa59f91-6d5d-4f11-97cf-bdab0773972b",
                                node_output_id:
                                  "32b2f0d3-fc4b-4e0c-997b-690de7de0912",
                              },
                              schema: {
                                anyOf: [
                                  { type: "number" },
                                  { type: "integer" },
                                ],
                              },
                            },
                          ],
                          trigger: {
                            id: "24d76ce4-c2b4-4988-88f8-f59ab3f09a34",
                            merge_behavior: "AWAIT_ATTRIBUTES",
                          },
                          definition: {
                            name: "Output1",
                            module: [
                              "new_workflow",
                              "nodes",
                              "agent",
                              "subtract",
                              "nodes",
                              "output",
                            ],
                          },
                          display_data: {
                            icon: "vellum:icon:circle-stop",
                            color: "teal",
                            width: 338,
                            height: 88,
                            z_index: 3,
                            position: { x: 2750.0, y: 210.0 },
                          },
                        },
                      ],
                      definition: {
                        name: "Subtract",
                        module: [
                          "new_workflow",
                          "nodes",
                          "agent",
                          "subtract",
                          "workflow",
                        ],
                      },
                      display_data: {
                        viewport: {
                          x: -928.6639662994166,
                          y: 96.75729099157488,
                          zoom: 0.5819831497083603,
                        },
                      },
                      output_values: [
                        {
                          value: {
                            type: "NODE_OUTPUT",
                            node_id: "d3d58aa4-ae05-4fc9-ba77-315cac5f4f06",
                            node_output_id:
                              "29b899b0-6e71-4e21-aaf2-5da484f9d088",
                          },
                          output_variable_id:
                            "29b899b0-6e71-4e21-aaf2-5da484f9d088",
                        },
                      ],
                    },
                  },
                },
              },
            },
            // COMPOSIO function
            {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: {
                  type: "COMPOSIO",
                  name: "github_create_issue",
                  toolkit: "GITHUB",
                  action: "GITHUB_CREATE_AN_ISSUE",
                  description: "Create a new issue in a GitHub repository",
                },
              },
            },
            // VELLUM_INTEGRATION function
            {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: {
                  type: "VELLUM_INTEGRATION",
                  provider: "COMPOSIO",
                  integration_name: "slack",
                  name: "slack_send_message",
                  description: "Send a message to a Slack channel",
                },
              },
            },
            // WORKFLOW_DEPLOYMENT function
            {
              type: "CONSTANT_VALUE",
              value: {
                type: "JSON",
                value: {
                  type: "WORKFLOW_DEPLOYMENT",
                  name: "my_deployed_workflow",
                  description: "A deployed workflow function",
                  deployment: "my-workflow-deployment",
                  release_tag: "production",
                },
              },
            },
          ],
        }
      );

      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "port-id",
        }),
      ];

      // WHEN we generate code for the ARRAY_REFERENCE format with all function types
      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [arrayReferenceFunctionsAttribute],
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

      // THEN the generated code should match the snapshot
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

  describe("examples", () => {
    it("should generate tool decorator with both inputs and examples", async () => {
      /**
       * Tests that a CODE_EXECUTION function with both inputs and examples
       * generates a tool decorator with both parameters.
       */

      // GIVEN a code execution function with both inputs and examples
      const codeExecutionFunction: FunctionArgs = {
        type: "CODE_EXECUTION",
        name: "get_current_weather",
        description: "",
        src: 'from typing import Annotated\n\n\ndef get_current_weather(\n    date_input: str,\n    location: Annotated[str, "The location to get the weather for"],\n    units: Annotated[str, "The unit of temperature"] = "fahrenheit",\n) -> str:\n    return f"The current weather on {date_input} in {location} is sunny with a temperature of 70 degrees {units}."\n',
        definition: {
          name: "get_current_weather",
          parameters: {
            type: "object",
            properties: {
              location: {
                type: "string",
                description: "The location to get the weather for",
              },
              units: {
                type: "string",
                description: "The unit of temperature",
                default: "fahrenheit",
              },
            },
            required: ["location"],
            examples: [
              { location: "San Francisco" },
              { location: "New York", units: "celsius" },
            ],
          },
          inputs: {
            date_input: {
              type: "WORKFLOW_INPUT",
              input_variable_id: "input-1",
            },
          },
        },
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
            value: [codeExecutionFunction],
          },
        }
      );

      const nodeData = toolCallingNodeFactory({
        nodePorts: nodePortData,
        nodeAttributes: [functionsAttribute],
      });

      // WHEN we create the node and generate the node file
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      const output = await writer.toStringFormatted();

      // THEN the generated code should include the tool decorator with both inputs and examples
      expect(output).toMatchSnapshot();
    });
  });
});
