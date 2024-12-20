import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { codeExecutionNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { CodeExecutionContext } from "src/context/node-context/code-execution-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { CodeExecutionNode } from "src/generators/nodes/code-execution-node";

describe("CodeExecutionNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: CodeExecutionNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodeData = codeExecutionNodeFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;
      workflowContext.addNodeContext(nodeContext);

      node = new CodeExecutionNode({
        workflowContext: workflowContext,
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

    it("getNodeDefinition", () => {
      expect(node.nodeContext.getNodeDefinition()).toMatchSnapshot();
    });
  });

  describe("code representation override", () => {
    it.each<"INLINE" | "STANDALONE" | undefined>([
      undefined,
      "STANDALONE",
      "INLINE",
    ])(
      "should generate the correct node class when the override is %s",
      async (override) => {
        workflowContext = workflowContextFactory({
          codeExecutionNodeCodeRepresentationOverride: override,
        });

        const nodeData = codeExecutionNodeFactory();

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as CodeExecutionContext;
        workflowContext.addNodeContext(nodeContext);

        node = new CodeExecutionNode({
          workflowContext: workflowContext,
          nodeContext,
        });

        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      }
    );
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
      });
      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as CodeExecutionContext;
      workflowContext.addNodeContext(nodeContext);

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
  });
});
