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
});
