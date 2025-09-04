import { Writer } from "@fern-api/python-ast/core/Writer";
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

  describe("function name casing in Python imports (APO-1372)", () => {
    describe("should preserve original camelCase function names in Python references", () => {
      beforeEach(async () => {
        const functions = [
          { type: "CODE_EXECUTION", name: "getCWD", src: "def getCWD(): pass" },
          {
            type: "CODE_EXECUTION",
            name: "parseJSON",
            src: "def parseJSON(): pass",
          },
          {
            type: "CODE_EXECUTION",
            name: "fetchData",
            src: "def fetchData(): pass",
          },
          {
            type: "CODE_EXECUTION",
            name: "XMLHttpRequest",
            src: "def XMLHttpRequest(): pass",
          },
        ];

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
              value: functions,
            },
          }
        );

        const nodeData = toolCallingNodeFactory({
          nodePorts: nodePortData,
          nodeAttributes: [functionsAttribute],
          label: "CasingTestNode",
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as GenericNodeContext;

        node = new GenericNode({
          workflowContext,
          nodeContext,
        });
      });

      it("getNodeFile preserves camelCase names and uses snake_case modules", async () => {
        node.getNodeFile().write(writer);
        const output = await writer.toStringFormatted();

        // Verify original function names are preserved in references
        expect(output).toContain("getCWD");
        expect(output).toContain("parseJSON");
        expect(output).toContain("fetchData");
        expect(output).toContain("XMLHttpRequest");

        // Verify snake_case module paths are used for imports
        expect(output).toContain("from .get_cwd import getCWD");
        expect(output).toContain("from .parse_json import parseJSON");
        expect(output).toContain("from .fetch_data import fetchData");
        expect(output).toContain("from .xmlhttp_request import XMLHttpRequest");
      });
    });

    describe("should handle edge cases in function names safely", () => {
      beforeEach(async () => {
        const functions = [
          {
            type: "CODE_EXECUTION",
            name: "valid_snake_case",
            src: "def valid_snake_case(): pass",
          },
          {
            type: "CODE_EXECUTION",
            name: "123invalid",
            src: "def _123invalid(): pass",
          },
          {
            type: "CODE_EXECUTION",
            name: "special-chars!",
            src: "def special_chars(): pass",
          },
          {
            type: "CODE_EXECUTION",
            name: "_underscore_start",
            src: "def _underscore_start(): pass",
          },
          {
            type: "CODE_EXECUTION",
            name: "normalFunction",
            src: "def normalFunction(): pass",
          },
        ];

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
              value: functions,
            },
          }
        );

        const nodeData = toolCallingNodeFactory({
          nodePorts: nodePortData,
          nodeAttributes: [functionsAttribute],
          label: "EdgeCaseTestNode",
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as GenericNodeContext;

        node = new GenericNode({
          workflowContext,
          nodeContext,
        });
      });

      it("getNodeFile handles invalid Python identifiers safely", async () => {
        node.getNodeFile().write(writer);
        const output = await writer.toStringFormatted();

        // Valid identifiers should be preserved
        expect(output).toContain("valid_snake_case");
        expect(output).toContain("normalFunction");

        // Invalid identifiers should be converted to safe versions
        expect(output).toContain("_123invalid"); // Numbers at start get prefix
        expect(output).toContain("special_chars"); // Special chars converted to snake_case
        expect(output).toContain("_underscore_start"); // Underscore start gets prefix

        // All should have corresponding snake_case module paths
        expect(output).toContain(
          "from .valid_snake_case import valid_snake_case"
        );
        expect(output).toContain("from ._123invalid import _123invalid");
        expect(output).toContain("from .special_chars import special_chars");
        expect(output).toContain(
          "from ._underscore_start import _underscore_start"
        );
        expect(output).toContain("from .normal_function import normalFunction");
      });
    });

    describe("should handle null/undefined function names gracefully", () => {
      it("should skip functions without names", async () => {
        const functions = [
          {
            type: "CODE_EXECUTION",
            name: "validFunction",
            src: "def validFunction(): pass",
          },
          { type: "CODE_EXECUTION", name: null, src: "def unnamed(): pass" },
          { type: "CODE_EXECUTION", name: "", src: "def empty(): pass" },
          {
            type: "CODE_EXECUTION",
            name: undefined,
            src: "def undefined(): pass",
          },
        ];

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
              value: functions,
            },
          }
        );

        const nodeData = toolCallingNodeFactory({
          nodePorts: nodePortData,
          nodeAttributes: [functionsAttribute],
          label: "NullTestNode",
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as GenericNodeContext;

        const node = new GenericNode({
          workflowContext,
          nodeContext,
        });

        expect(() => {
          node.getNodeFile().write(writer);
        }).not.toThrow();

        const output = await writer.toStringFormatted();

        // Only valid function should be included
        expect(output).toContain("validFunction");
        expect(output).toContain("from .valid_function import validFunction");

        // Invalid/empty names should not appear
        expect(output).not.toContain("null");
        expect(output).not.toContain("undefined");
        expect(output).not.toContain('""');
      });
    });

    describe("regression test for the original bug", () => {
      it("should not convert camelCase function names to snake_case in references", async () => {
        // This test specifically reproduces the original APO-1372 issue
        const functions = [
          {
            type: "CODE_EXECUTION",
            name: "getCwd",
            src: "def getCwd(): return os.getcwd()",
          },
        ];

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
              value: functions,
            },
          }
        );

        const nodeData = toolCallingNodeFactory({
          nodePorts: nodePortData,
          nodeAttributes: [functionsAttribute],
          label: "RegressionTestNode",
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
        const output = await writer.toStringFormatted();

        // The bug was that this would generate:
        // python.reference({ name: "get_cwd", modulePath: [".get_cwd"] })
        // Instead it should generate:
        // python.reference({ name: "getCwd", modulePath: [".get_cwd"] })

        expect(output).toContain("getCwd"); // Original camelCase name preserved
        expect(output).toContain("from .get_cwd import getCwd"); // Snake case module path

        // Ensure we don't have the bug where both name and module were snake_case
        expect(output).not.toMatch(/name.*get_cwd.*modulePath.*get_cwd/);
      });
    });
  });
});
