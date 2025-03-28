import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  genericNodeFactory,
  inlinePromptNodeDataInlineVariantFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { GenericNode } from "src/generators/nodes/generic-node";
import { AdornmentNode, NodeAttribute } from "src/types/vellum";

describe("GenericNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: GenericNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
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
      const nodeData = genericNodeFactory();

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

  describe("basic with node output as attribute", () => {
    beforeEach(async () => {
      const referencedNode = inlinePromptNodeDataInlineVariantFactory({
        blockType: "JINJA",
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
            nodeOutputId: referencedNode.data.outputId,
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

      const nodeData = genericNodeFactory({
        label: "MyCustomNode",
        adornments: adornments,
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
});
