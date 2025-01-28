import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { codeExecutionNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { CodeExecutionContext } from "src/context/node-context/code-execution-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { CodeExecutionNode } from "src/generators/nodes/code-execution-node";
import { NodeInputValuePointerRule } from "src/types/vellum";

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
  describe("with runtime set", () => {
    it.each<"PYTHON_3_11_6" | "TYPESCRIPT_5_3_3">([
      "PYTHON_3_11_6",
      "TYPESCRIPT_5_3_3",
    ])("should generate the correct standalone file %s", async (override) => {
      workflowContext = workflowContextFactory({
        codeExecutionNodeCodeRepresentationOverride: "STANDALONE",
      });

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
        runtime: override,
      });

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
});
