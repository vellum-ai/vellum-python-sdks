import { WorkflowContext } from "src/context";
import { GenericNodeDisplayData } from "src/generators/generic-node-display-data";
import { GenericNodeDisplayData as GenericNodeDisplayDataType } from "src/types/vellum";

describe("GenericNodeDisplayData", () => {
  let mockWorkflowContext: WorkflowContext;

  beforeEach(() => {
    mockWorkflowContext = {} as WorkflowContext;
  });

  describe("icon field generation", () => {
    it("should include icon in generated code when icon is provided", () => {
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
        icon: "vellum:icon:star",
      };

      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

      expect(code).toContain('icon="vellum:icon:star"');
    });

    it("should not include icon in generated code when icon is undefined", () => {
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
      };

      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

      expect(code).not.toContain("icon=");
    });
  });

  describe("color field generation", () => {
    it("should include color in generated code when color is provided", () => {
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
        color: "navy",
      };

      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

      expect(code).toContain('color="navy"');
    });

    it("should not include color in generated code when color is undefined", () => {
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
      };

      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

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

  describe("icon and color together", () => {
    it("should include both icon and color in generated code when both are provided", () => {
      const nodeDisplayData: GenericNodeDisplayDataType = {
        position: { x: 0, y: 0 },
        icon: "vellum:icon:cog",
        color: "navy",
      };

      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

      expect(code).toContain('icon="vellum:icon:cog"');
      expect(code).toContain('color="navy"');
    });
  });

  describe("empty display data", () => {
    it("should return empty string when no display data is provided", () => {
      const generator = new GenericNodeDisplayData({
        nodeDisplayData: undefined,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

      expect(code).toBe("");
    });

    it("should return empty string when only null/undefined fields are provided", () => {
      const nodeDisplayData: GenericNodeDisplayDataType = {
        icon: null,
        color: null,
        // position and z_index undefined, should not generate any content
      };

      const generator = new GenericNodeDisplayData({
        nodeDisplayData,
        workflowContext: mockWorkflowContext,
      });

      const code = generator.toString();

      expect(code).toBe("");
    });
  });
});
