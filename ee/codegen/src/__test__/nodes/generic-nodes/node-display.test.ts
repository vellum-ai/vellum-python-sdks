import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { GenericNode } from "src/generators/nodes/generic-node";

describe("NodeDisplay", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    // Add the input variables that the generic node factory uses
    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "input-1",
          key: "input_1",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  describe("with icon and color", () => {
    it("generates Display nested class with both fields", async () => {
      const nodeData = genericNodeFactory({
        label: "MyCustomNode",
      });

      // Add display data with icon and color
      nodeData.displayData = {
        icon: "🎨",
        color: "#FF5733",
      };

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      const nodeClass = node.generateNodeClass();
      nodeClass.write(writer);

      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("with only icon", () => {
    it("generates Display nested class with icon field", async () => {
      const nodeData = genericNodeFactory({
        label: "MyCustomNode",
      });

      // Add display data with only icon
      nodeData.displayData = {
        icon: "🔧",
      };

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      const nodeClass = node.generateNodeClass();
      nodeClass.write(writer);

      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("with only color", () => {
    it("generates Display nested class with color field", async () => {
      const nodeData = genericNodeFactory({
        label: "MyCustomNode",
      });

      // Add display data with only color
      nodeData.displayData = {
        color: "#00FF00",
      };

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      const nodeClass = node.generateNodeClass();
      nodeClass.write(writer);

      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("without icon or color", () => {
    it("does not generate Display nested class", async () => {
      const nodeData = genericNodeFactory({
        label: "MyCustomNode",
      });

      // Display data without icon or color
      nodeData.displayData = {
        position: { x: 100, y: 200 },
      };

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      const nodeClass = node.generateNodeClass();
      nodeClass.write(writer);

      const generated = await writer.toStringFormatted();

      // Verify no Display class is generated
      expect(generated).not.toContain("class Display");
    });
  });

  describe("with null icon and color", () => {
    it("does not generate Display nested class", async () => {
      const nodeData = genericNodeFactory({
        label: "MyCustomNode",
      });

      // Explicit null values
      nodeData.displayData = {
        icon: null,
        color: null,
      };

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      const nodeClass = node.generateNodeClass();
      nodeClass.write(writer);

      const generated = await writer.toStringFormatted();

      // Verify no Display class is generated
      expect(generated).not.toContain("class Display");
    });
  });
});
