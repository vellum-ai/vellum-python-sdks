import { WorkflowContext } from "src/context";
import { GenericNodeDisplayData } from "src/generators/generic-node-display-data";
import { GenericNodeDisplayData as GenericNodeDisplayDataType } from "src/types/vellum";

describe("GenericNodeDisplayData", () => {
  let mockWorkflowContext: WorkflowContext;

  beforeEach(() => {
    mockWorkflowContext = {} as WorkflowContext;
  });

  describe("icon and color field generation", () => {
    it("should not include icon in generated code even when icon is provided", () => {
      /**
       * Tests that icon is not generated in GenericNodeDisplayData since it's now generated in BaseNode.Display.
       */
      // GIVEN a node display data with icon
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
        icon: "vellum:icon:star",
      };

      // WHEN we generate the code
      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });
      const code = generator.toString();

      // THEN icon should not be included
      expect(code).not.toContain("icon=");
    });

    it("should not include color in generated code even when color is provided", () => {
      /**
       * Tests that color is not generated in GenericNodeDisplayData since it's now generated in BaseNode.Display.
       */
      // GIVEN a node display data with color
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
        color: "navy",
      };

      // WHEN we generate the code
      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });
      const code = generator.toString();

      // THEN color should not be included
      expect(code).not.toContain("color=");
    });
  });

  describe("z_index field generation", () => {
    it("should include z_index in generated code when z_index is provided", () => {
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
        z_index: 5,
      };

      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

      expect(code).toContain("z_index=5");
    });

    it("should not include z_index in generated code when z_index is undefined", () => {
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
      };

      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

      expect(code).not.toContain("z_index=");
    });
  });

  describe("empty display data", () => {
    it("should return empty string when no display data is provided", () => {
      /**
       * Tests that no code is generated when display data is undefined.
       */
      // GIVEN no display data
      // WHEN we generate the code
      const generator = new GenericNodeDisplayData({
        nodeDisplayData: undefined,
        workflowContext: mockWorkflowContext,
      });
      const code = generator.toString();

      // THEN the code should be empty
      expect(code).toBe("");
    });

    it("should return empty string when only icon and color are provided", () => {
      /**
       * Tests that no code is generated when only icon and color are provided since they're now generated in BaseNode.Display.
       */
      // GIVEN display data with only icon and color
      const nodeDisplayData: GenericNodeDisplayDataType = {
        icon: "vellum:icon:cog",
        color: "navy",
      };

      // WHEN we generate the code
      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });
      const code = generator.toString();

      // THEN the code should be empty since icon and color are no longer generated here
      expect(code).toBe("");
    });
  });
});
