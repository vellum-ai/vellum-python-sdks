import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  genericNodeFactory,
  inlinePromptNodeDataInlineVariantFactory,
  nodePortFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { GenericNode } from "src/generators/nodes/generic-node";
import {
  AdornmentNode,
  NodeAttribute,
  WorkflowValueDescriptor,
} from "src/types/vellum";

describe("GenericNode", () => {
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
          key: "count",
          type: "NUMBER",
        },
        workflowContext,
      })
    );
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodePortData = [
        nodePortFactory({
          id: "2544f9e4-d6e6-4475-b6a9-13393115d77c",
        }),
      ];
      const nodeData = genericNodeFactory({
        nodePorts: nodePortData,
        id: "9dc95b5d-1467-4b17-abb0-449d1aac6aec",
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

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic without node outputs should skip node outputs class", () => {
    beforeEach(async () => {
      const nodeData = genericNodeFactory({
        nodeOutputs: [],
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

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with node output as attribute", () => {
    beforeEach(async () => {
      const referencedNode = inlinePromptNodeDataInlineVariantFactory({
        blockType: "JINJA",
      }).build();

      await createNodeContext({
        workflowContext,
        nodeData: referencedNode,
      });

      const nodeAttributes: NodeAttribute[] = [
        {
          id: "attr-1-id",
          name: "default-attribute",
          value: {
            type: "NODE_OUTPUT",
            nodeId: referencedNode.id,
            nodeOutputId: referencedNode.data.outputId,
          },
        },
      ];

      const nodePortData = [
        nodePortFactory({
          id: "2544f9e4-d6e6-4475-b6a9-13393115d77c",
        }),
      ];

      const nodeData = genericNodeFactory({
        id: "bed8d22e-4835-41d9-ad81-e78a4b0e7ae0",
        label: "MyCustomNode",
        nodeAttributes: nodeAttributes,
        nodePorts: nodePortData,
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

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with generic node output as attribute", () => {
    beforeEach(async () => {
      const nodeOutputId = uuidv4();
      const referencedNode = genericNodeFactory({
        label: "ReferencedNode",
        nodeOutputs: [
          {
            id: nodeOutputId,
            name: "output",
            type: "STRING",
          },
        ],
      });
      await createNodeContext({
        workflowContext,
        nodeData: referencedNode,
      });

      const nodeAttributes: NodeAttribute[] = [
        {
          id: "attr-1",
          name: "default-attribute",
          value: {
            type: "NODE_OUTPUT",
            nodeId: referencedNode.id,
            nodeOutputId: nodeOutputId,
          },
        },
      ];

      const nodeData = genericNodeFactory({
        label: "MyCustomNode",
        nodeAttributes: nodeAttributes,
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

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with adornments", () => {
    beforeEach(async () => {
      const adornments: AdornmentNode[] = [
        {
          id: "adornment-1",
          label: "TryNodeLabel",
          base: {
            name: "TryNode",
            module: [
              "vellum",
              "workflows",
              "nodes",
              "core",
              "try_node",
              "node",
            ],
          },
          attributes: [
            {
              id: "attr-1",
              name: "on_error_code",
              value: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "USER_DEFINED_ERROR",
                },
              },
            },
          ],
        },
        {
          id: "adornment-2",
          label: "MapNodeLabel",
          base: {
            name: "MapNode",
            module: [
              "vellum",
              "workflows",
              "nodes",
              "core",
              "map_node",
              "node",
            ],
          },
          attributes: [
            {
              id: "attr-1",
              name: "items",
              value: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "ARRAY",
                  value: [
                    {
                      type: "NUMBER",
                      value: 1,
                    },
                    {
                      type: "NUMBER",
                      value: 2,
                    },
                  ],
                },
              },
            },
          ],
        },
        {
          id: "adornment-3",
          label: "RetryNodeLabel",
          base: {
            name: "RetryNode",
            module: [
              "vellum",
              "workflows",
              "nodes",
              "core",
              "retry_node",
              "node",
            ],
          },
          attributes: [
            {
              id: "attr-1",
              name: "max_attempts",
              value: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "NUMBER",
                  value: 3,
                },
              },
            },
          ],
        },
      ];

      const nodePortData = [
        nodePortFactory({
          id: "2544f9e4-d6e6-4475-b6a9-13393115d77c",
        }),
      ];

      const nodeData = genericNodeFactory({
        id: "75ce71d3-d50b-4c8f-9b38-eee8c8362a92",
        label: "MyCustomNode",
        adornments: adornments,
        nodePorts: nodePortData,
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

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with default node trigger", () => {
    it("getNodeFile", async () => {
      const nodeData = genericNodeFactory({
        nodeTrigger: {
          id: "trigger-1",
          mergeBehavior: "AWAIT_ATTRIBUTES",
        },
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with with access field in ports", () => {
    it("getNodeFile", async () => {
      const nodeData = genericNodeFactory({
        nodePorts: [
          {
            id: "port-1",
            name: "access",
            type: "IF",
            expression: {
              type: "BINARY_EXPRESSION",
              operator: "accessField",
              lhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "JSON",
                  value: {
                    foo: "bar",
                  },
                },
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "foo",
                },
              },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with custom base", () => {
    it("getNodeFile", async () => {
      const nodeData = genericNodeFactory({
        base: {
          name: "MockNetworkingClient",
          module: ["path", "to", "mock_networking_client"],
        },
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with custom, same module, base", () => {
    it("getNodeFile", async () => {
      workflowContext = workflowContextFactory({
        moduleName: "my.custom.path",
      });

      const nodeData = genericNodeFactory({
        base: {
          name: "MockNetworkingClient",
          module: ["my", "custom", "path", "nodes", "mock_networking_client"],
        },
        nodeAttributes: [],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with only `pass`", () => {
    it("getNodeFile", async () => {
      const nodeData = genericNodeFactory({
        nodeAttributes: [],
        nodeOutputs: [],
        nodeTrigger: {
          id: uuidv4(),
          mergeBehavior: "AWAIT_ATTRIBUTES",
        },
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with a JSON output", () => {
    it("getNodeFile", async () => {
      const nodeData = genericNodeFactory({
        nodeAttributes: [],
        nodeOutputs: [
          {
            id: uuidv4(),
            name: "output",
            type: "JSON",
            value: undefined,
          },
        ],
        nodeTrigger: {
          id: uuidv4(),
          mergeBehavior: "AWAIT_ATTRIBUTES",
        },
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with invalid coalesce binary expression", () => {
    beforeEach(async () => {
      const nodeAttributes: NodeAttribute[] = [
        {
          id: "attr-1",
          name: "coalesce-attribute",
          value: {
            type: "BINARY_EXPRESSION",
            operator: "coalesce",
            lhs: null,
            rhs: {
              type: "CONSTANT_VALUE",
              value: {
                type: "STRING",
                value: "fallback_value",
              },
            },
          } as unknown as WorkflowValueDescriptor,
        },
      ];

      const nodeData = genericNodeFactory({
        label: "TestCoalesceNode",
        nodeAttributes: nodeAttributes,
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

    it("should handle null LHS in coalesce expression gracefully", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with invalid blank unary expression", () => {
    beforeEach(async () => {
      const nodeAttributes: NodeAttribute[] = [
        {
          id: "attr-1",
          name: "blank-attribute",
          value: {
            type: "UNARY_EXPRESSION",
            operator: "blank",
            lhs: null,
          } as unknown as WorkflowValueDescriptor,
        },
      ];

      const nodeData = genericNodeFactory({
        label: "TestBlankNode",
        nodeAttributes: nodeAttributes,
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

    it("should handle null LHS in blank expression gracefully", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with invalid notBlank unary expression", () => {
    beforeEach(async () => {
      const nodeAttributes: NodeAttribute[] = [
        {
          id: "attr-2",
          name: "notBlank-attribute",
          value: {
            type: "UNARY_EXPRESSION",
            operator: "notBlank",
            lhs: null,
          } as unknown as WorkflowValueDescriptor,
        },
      ];

      const nodeData = genericNodeFactory({
        label: "TestNotBlankNode",
        nodeAttributes: nodeAttributes,
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

    it("should handle null LHS in notBlank expression gracefully", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with environment variable reference as attribute", () => {
    beforeEach(async () => {
      const nodeAttributes: NodeAttribute[] = [
        {
          id: "attr-1",
          name: "api-key-attribute",
          value: {
            type: "ENVIRONMENT_VARIABLE",
            environmentVariable: "API_KEY",
          },
        },
      ];

      const nodeData = genericNodeFactory({
        label: "TestEnvironmentVariableNode",
        nodeAttributes: nodeAttributes,
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

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("generic node with no attributes, no ports, no outputs", () => {
    /**
     * Tests that a generic node with no attributes, no ports, and no outputs generates correctly.
     */
    it("getNodeFile", async () => {
      // GIVEN a generic node with no attributes, default trigger, and no outputs
      const nodeData = genericNodeFactory({
        nodeAttributes: [],
        nodeOutputs: [],
        nodeTrigger: {
          id: uuidv4(),
          mergeBehavior: "AWAIT_ATTRIBUTES",
        },
        displayData: {
          position: {
            x: 200.0,
            y: -50.0,
          },
        },
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      // WHEN we generate the node file
      node.getNodeFile().write(writer);

      // THEN the output should match the snapshot
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
