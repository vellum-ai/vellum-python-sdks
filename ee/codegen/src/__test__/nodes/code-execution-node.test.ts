import { mkdir, readFile } from "fs/promises";
import { join } from "path";

import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuid } from "uuid";
import { SecretTypeEnum, WorkspaceSecretRead } from "vellum-ai/api";
import { WorkspaceSecrets } from "vellum-ai/api/resources/workspaceSecrets/client/Client";
import { VellumError } from "vellum-ai/errors";
import { beforeEach, describe } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import {
  codeExecutionNodeFactory,
  nodeInputFactory,
  nodePortFactory,
} from "src/__test__/helpers/node-data-factories";
import { makeTempDir } from "src/__test__/helpers/temp-dir";
import { createNodeContext, WorkflowContext } from "src/context";
import { CodeExecutionContext } from "src/context/node-context/code-execution-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { CodeExecutionNode } from "src/generators/nodes/code-execution-node";
import {
  NodeInput,
  NodeInputValuePointerRule,
  NodePort,
} from "src/types/vellum";

describe("CodeExecutionNode", () => {
  let tempDir: string;
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: CodeExecutionNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory({
      strict: false,
    });
    writer = new Writer();
    tempDir = makeTempDir("code-node-test");
    await mkdir(tempDir, { recursive: true });
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodeData = codeExecutionNodeFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;

      node = new CodeExecutionNode({
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

  describe("basic representation", () => {
    it("should accept int and float", async () => {
      const nodeData = codeExecutionNodeFactory({
        codeOutputValueType: "NUMBER",
      }).build();
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;
      node = new CodeExecutionNode({
        workflowContext: workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe.each([
    ["Base case", "print('Hello, World!')"],
    [
      "Escaped case",
      "async function main(inputs: {\n  question: string\n}) {\n  inputs = {\n" +
        '"question": "{\\"text_explanation\\":\\"First, \\\\\\\\(\\\\\\\\frac{1}{40}\\\\\\\\).\\\\"\n  }\n' +
        "const test = \"\\frac\".replace(/\\\\frac/g, '\\\\dfrac');\n  return {};\n} \n",
    ],
  ])("code representation: %s", (_, code) => {
    it("should generate the correct node class", async () => {
      workflowContext = workflowContextFactory({
        absolutePathToOutputDirectory: tempDir,
        moduleName: "code",
      });

      const nodeData = codeExecutionNodeFactory({
        code,
        packages: [
          { name: "my-package", version: "1.0.0", repository: "test-repo" },
        ],
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;

      node = new CodeExecutionNode({
        workflowContext: workflowContext,
        nodeContext,
      });

      // Always do full persist to check write logic
      await node.persist();

      expect(
        await readFile(
          join(tempDir, "code", "nodes", "code_execution_node", "__init__.py"),
          "utf-8"
        )
      ).toMatchSnapshot();
    });
  });

  describe("failure cases", () => {
    it("rejects if code input is not a constant string", async () => {
      const nodeData = codeExecutionNodeFactory({
        codeInputValueRule: {
          type: "CONSTANT_VALUE",
          data: {
            type: "JSON",
            value: null,
          },
        },
      }).build();
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;

      expect(() => {
        new CodeExecutionNode({
          workflowContext: workflowContext,
          nodeContext,
        });
      }).toThrow(
        new NodeAttributeGenerationError(
          "Expected to find code input with constant string value"
        )
      );
    });

    it.each<NodeInput>([
      nodeInputFactory({
        value: {
          type: "CONSTANT_VALUE",
          data: {
            type: "NUMBER",
            value: 1,
          },
        },
      }),
      nodeInputFactory({
        value: {
          type: "CONSTANT_VALUE",
          data: {
            type: "STRING",
            value: "INVALID_RUNTIME",
          },
        },
      }),
    ])(
      "fallback to python 3.11.6 if runtime input is not valid",
      async (runtimeInput) => {
        const workflowContext = workflowContextFactory({
          strict: false,
        });
        const nodeData = codeExecutionNodeFactory({
          runtimeInput,
        }).build();
        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as CodeExecutionContext;

        node = new CodeExecutionNode({
          workflowContext,
          nodeContext,
        });

        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      }
    );
  });

  describe("with runtime set", () => {
    it.each<"PYTHON_3_11_6" | "TYPESCRIPT_5_3_3">([
      "PYTHON_3_11_6",
      "TYPESCRIPT_5_3_3",
    ])("should generate the correct standalone file %s", async (override) => {
      workflowContext = workflowContextFactory();

      const overrideInputValue: NodeInputValuePointerRule = {
        type: "CONSTANT_VALUE",
        data: {
          type: "STRING",
          value:
            override == "TYPESCRIPT_5_3_3"
              ? "async function main(inputs: {\n\n}): Promise<number> {\n\n  return;\n}"
              : "def main(inputs):\n  return",
        },
      };

      const nodeData = codeExecutionNodeFactory({
        codeInputValueRule: overrideInputValue,
        runtimeInput: nodeInputFactory({
          key: "runtime",
          value: {
            type: "CONSTANT_VALUE",
            data: {
              type: "STRING",
              value: override,
            },
          },
        }),
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;

      node = new CodeExecutionNode({
        workflowContext: workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  const mockWorkspaceSecretDefinition = (workspaceSecret: {
    id: string;
    name: string;
  }) => ({
    id: workspaceSecret.id,
    name: workspaceSecret.name,
    modified: new Date(),
    label: "mocked-workspace-secret-label",
    description: "mocked-workspace-secret-description",
    secretType: SecretTypeEnum.UserDefined,
  });

  const createNode = async ({
    workspaceSecret,
  }: {
    workspaceSecret: { id: string; name: string };
  }) => {
    vi.spyOn(WorkspaceSecrets.prototype, "retrieve").mockResolvedValue(
      mockWorkspaceSecretDefinition(
        workspaceSecret
      ) as unknown as WorkspaceSecretRead
    );

    const nodeData = codeExecutionNodeFactory().build();
    const bearer_input = uuid();
    nodeData.inputs.push({
      id: bearer_input,
      key: "secret_arg",
      value: {
        rules: [
          {
            type: "WORKSPACE_SECRET",
            data: {
              type: "STRING",
              workspaceSecretId: workspaceSecret.id,
            },
          },
        ],
        combinator: "OR",
      },
    });
    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as CodeExecutionContext;

    return new CodeExecutionNode({
      workflowContext,
      nodeContext,
    });
  };

  describe("basic secret node", () => {
    it.each([{ id: "1234", name: "test-secret" }])(
      "secret ids should show names",
      async (workspaceSecret: { id: string; name: string }) => {
        const node = await createNode({ workspaceSecret });
        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      }
    );

    it("should be resilient to invalid secret ids", async () => {
      vi.spyOn(WorkspaceSecrets.prototype, "retrieve").mockImplementation(() =>
        // @ts-ignore
        Promise.reject(
          new VellumError({ message: "not found", statusCode: 404 })
        )
      );

      const nodeData = codeExecutionNodeFactory().build();
      const bearer_input = uuid();
      nodeData.inputs.push({
        id: bearer_input,
        key: "secret_arg",
        value: {
          rules: [
            {
              type: "WORKSPACE_SECRET",
              data: {
                type: "STRING",
                workspaceSecretId: "5678",
              },
            },
          ],
          combinator: "OR",
        },
      });
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;

      const node = new CodeExecutionNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();

      const errors = workflowContext.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0]?.message).toContain(
        'Workspace Secret mapped to input "secret_arg" not found'
      );
      expect(errors[0]?.severity).toBe("WARNING");
    });
  });

  describe("log output id", () => {
    it("should not generate log output id if not given", async () => {
      const nodeData = codeExecutionNodeFactory({
        generateLogOutputId: false,
      }).build();
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;

      node = new CodeExecutionNode({
        workflowContext: workflowContext,
        nodeContext,
      });

      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with ports", () => {
    const ifPortId = "3e9a8943-db9d-4586-a657-3f4ce1c1b595";
    const elsePortId = "27aee210-2375-43e0-8dad-8856d9ff3cfb";

    describe("with ports referencing current node output", () => {
      beforeEach(async () => {
        const codeExecutionNodeData = codeExecutionNodeFactory();

        const nodePortsData: NodePort[] = [
          nodePortFactory({
            type: "IF",
            id: ifPortId,
            expression: {
              type: "BINARY_EXPRESSION",
              operator: "=",
              lhs: {
                type: "NODE_OUTPUT",
                nodeId: codeExecutionNodeData.nodeData.id,
                nodeOutputId: codeExecutionNodeData.nodeData.data.outputId,
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "Hello, World!",
                },
              },
            },
          }),
          nodePortFactory({
            type: "ELSE",
            id: elsePortId,
          }),
        ];

        const nodeData = codeExecutionNodeData.withPorts(nodePortsData).build();

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as CodeExecutionContext;

        node = new CodeExecutionNode({
          workflowContext,
          nodeContext,
        });
      });

      it("getNodeFile", async () => {
        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });
    });

    describe("with ports referencing upstream node output", () => {
      beforeEach(async () => {
        const upstreamNodeId = uuid();
        const upstreamOutputId = uuid();
        const upstreamCodeExecNodeData = codeExecutionNodeFactory({
          id: upstreamNodeId,
          outputId: upstreamOutputId,
          label: "Upstream code node",
        }).build();

        (await createNodeContext({
          workflowContext,
          nodeData: upstreamCodeExecNodeData,
        })) as CodeExecutionContext;

        const codeExecutionNodeData = codeExecutionNodeFactory();

        const nodePortsData: NodePort[] = [
          nodePortFactory({
            type: "IF",
            id: ifPortId,
            expression: {
              type: "BINARY_EXPRESSION",
              operator: "=",
              lhs: {
                type: "NODE_OUTPUT",
                nodeId: upstreamNodeId,
                nodeOutputId: upstreamOutputId,
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "Upstream node",
                },
              },
            },
          }),
          nodePortFactory({
            type: "ELSE",
            id: elsePortId,
          }),
        ];

        const nodeData = codeExecutionNodeData.withPorts(nodePortsData).build();

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as CodeExecutionContext;

        node = new CodeExecutionNode({
          workflowContext,
          nodeContext,
        });
      });

      it("getNodeFile", async () => {
        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });
    });
  });
  describe("with environment variable input", () => {
    it("should generate environment variable input", async () => {
      const nodeData = codeExecutionNodeFactory().build();
      nodeData.inputs.push({
        id: "b23a576d-bea6-4dbc-84aa-72038793a85d",
        key: "test_env_var",
        value: {
          rules: [
            {
              data: {
                environmentVariable: "TEST_ENV_VAR",
              },
              type: "ENVIRONMENT_VARIABLE",
            },
          ],
          combinator: "OR",
        },
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;

      node = new CodeExecutionNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
