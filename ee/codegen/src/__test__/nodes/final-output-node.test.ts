import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { finalOutputNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { FinalOutputNodeContext } from "src/context/node-context/final-output-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { FinalOutputNode } from "src/generators/nodes/final-output-node";

describe("FinalOutputNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: FinalOutputNode;

  beforeEach(() => {
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory();
      const nodeData = finalOutputNodeFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as FinalOutputNodeContext;

      node = new FinalOutputNode({
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

  describe("should codegen successfully without node input", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });
      const nodeData = finalOutputNodeFactory({ includeInput: false }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as FinalOutputNodeContext;

      node = new FinalOutputNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(workflowContext.getErrors()).toEqual([
        new NodeAttributeGenerationError(
          'No input found named "node_input"',
          "WARNING"
        ),
      ]);
      expect(workflowContext.getErrors()[0]?.severity).toEqual("WARNING");
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("should generate unique class names when mixing defined and undefined class names", () => {
    let nodeWithDefinition: FinalOutputNode;
    let nodeWithoutDefinition1: FinalOutputNode;
    let nodeWithoutDefinition2: FinalOutputNode;

    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });

      // First node: has a definition with class name "FinalOutput"
      const nodeDataWithDefinition = finalOutputNodeFactory({
        id: "node-with-definition",
        name: "final_output",
        label: "Final Output",
      }).build();
      nodeDataWithDefinition.definition = {
        name: "FinalOutput",
        module: ["test", "nodes", "final_output"],
      };

      // Second node: no definition, should get "FinalOutput1"
      const nodeDataWithoutDefinition1 = finalOutputNodeFactory({
        id: "node-without-definition-1",
        name: "text",
        label: "Final Output",
      }).build();
      nodeDataWithoutDefinition1.definition = undefined;

      // Third node: no definition, should get "FinalOutput2"
      const nodeDataWithoutDefinition2 = finalOutputNodeFactory({
        id: "node-without-definition-2",
        name: "chat_history",
        label: "Final Output",
      }).build();
      nodeDataWithoutDefinition2.definition = undefined;

      // Create contexts for all three nodes
      const nodeContextWithDefinition = (await createNodeContext({
        workflowContext,
        nodeData: nodeDataWithDefinition,
      })) as FinalOutputNodeContext;

      const nodeContextWithoutDefinition1 = (await createNodeContext({
        workflowContext,
        nodeData: nodeDataWithoutDefinition1,
      })) as FinalOutputNodeContext;

      const nodeContextWithoutDefinition2 = (await createNodeContext({
        workflowContext,
        nodeData: nodeDataWithoutDefinition2,
      })) as FinalOutputNodeContext;

      nodeWithDefinition = new FinalOutputNode({
        workflowContext,
        nodeContext: nodeContextWithDefinition,
      });
      nodeWithoutDefinition1 = new FinalOutputNode({
        workflowContext,
        nodeContext: nodeContextWithoutDefinition1,
      });
      nodeWithoutDefinition2 = new FinalOutputNode({
        workflowContext,
        nodeContext: nodeContextWithoutDefinition2,
      });
    });
    it("getNodeFile", async () => {
      nodeWithDefinition.getNodeFile().write(writer);
      nodeWithoutDefinition1.getNodeFile().write(writer);
      nodeWithoutDefinition2.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it("getNodeDisplayFile", async () => {
      nodeWithDefinition.getNodeDisplayFile().write(writer);
      nodeWithoutDefinition1.getNodeDisplayFile().write(writer);
      nodeWithoutDefinition2.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("should codegen deduplicated output class", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });
      const nodeData = finalOutputNodeFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as FinalOutputNodeContext;

      node = new FinalOutputNode({
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

  describe("should use schema field for type annotation when available", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });
      const nodeData = finalOutputNodeFactory().build();

      nodeData.outputs = [
        {
          id: "output-id",
          name: "value",
          type: "ARRAY",
          schema: {
            type: "array",
            items: {
              type: "string",
            },
          },
        },
      ];

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as FinalOutputNodeContext;

      node = new FinalOutputNode({
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
