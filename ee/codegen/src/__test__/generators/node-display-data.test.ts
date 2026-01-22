import { WorkflowContext } from "src/context";
import { NodeDisplayData } from "src/generators/node-display-data";

describe("NodeDisplayData", () => {
  let mockWorkflowContext: WorkflowContext;

  beforeEach(() => {
    mockWorkflowContext = {} as WorkflowContext;
  });

  describe("icon and color field generation", () => {
    it("should not include icon in generated code even when icon is provided", () => {
      /**
       * Tests that icon is not generated in NodeDisplayData since it's now generated in BaseNode.Display.
       */
      // GIVEN a node display data with icon
      const nodeDisplayData = {
        position: { x: 0, y: 0 },
        icon: "vellum:icon:star",
      };

      // WHEN we generate the code
      const generator = new NodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });
      const code = generator.toString();

      // THEN icon should not be included
      expect(code).not.toContain("icon=");
    });

    it("should not include color in generated code even when color is provided", () => {
      /**
       * Tests that color is not generated in NodeDisplayData since it's now generated in BaseNode.Display.
       */
      // GIVEN a node display data with color
      const nodeDisplayData = {
        position: { x: 0, y: 0 },
        color: "navy",
      };

      // WHEN we generate the code
      const generator = new NodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });
      const code = generator.toString();

      // THEN color should not be included
      expect(code).not.toContain("color=");
    });

    it("should not include icon or color in generated code even when both are provided", () => {
      /**
       * Tests that neither icon nor color are generated in NodeDisplayData since they're now generated in BaseNode.Display.
       */
      // GIVEN a node display data with both icon and color
      const nodeDisplayData = {
        position: { x: 0, y: 0 },
        icon: "vellum:icon:cog",
        color: "navy",
      };

      // WHEN we generate the code
      const generator = new NodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });
      const code = generator.toString();

      // THEN neither icon nor color should be included
      expect(code).not.toContain("icon=");
      expect(code).not.toContain("color=");
    });
  });
});
