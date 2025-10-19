import { describe, it, expect } from "vitest";

import { WorkflowTrigger } from "src/types/vellum";
import { getTriggerClassInfo } from "src/utils/triggers";

describe("getTriggerClassInfo", () => {
  it("should return correct info for MANUAL trigger", () => {
    const trigger: WorkflowTrigger = {
      id: "manual-trigger-id",
      type: "MANUAL",
      attributes: [],
    };

    const result = getTriggerClassInfo(trigger);

    expect(result).toEqual({
      className: "ManualTrigger",
      modulePath: ["vellum", "workflows", "triggers", "manual"],
    });
  });

  it("should return correct info for INTEGRATION trigger", () => {
    const trigger: WorkflowTrigger = {
      id: "integration-trigger-id",
      type: "INTEGRATION",
      attributes: [
        { id: "attr-1", name: "message", value: null },
        { id: "attr-2", name: "channel", value: null },
      ],
      class_name: "SlackMessageTrigger",
      module_path: [
        "ee",
        "vellum_ee",
        "workflows",
        "display",
        "tests",
        "workflow_serialization",
        "test_vellum_integration_trigger_serialization",
      ],
    };

    const result = getTriggerClassInfo(trigger);

    expect(result).toEqual({
      className: "SlackMessageTrigger",
      modulePath: [
        "ee",
        "vellum_ee",
        "workflows",
        "display",
        "tests",
        "workflow_serialization",
        "test_vellum_integration_trigger_serialization",
      ],
    });
  });

  it("should return null for INTEGRATION trigger without class_name", () => {
    const trigger: WorkflowTrigger = {
      id: "integration-trigger-id",
      type: "INTEGRATION",
      attributes: [],
      // Missing class_name and module_path
    };

    const result = getTriggerClassInfo(trigger);

    expect(result).toBeNull();
  });

  it("should return null for unknown trigger type", () => {
    const trigger: WorkflowTrigger = {
      id: "unknown-trigger-id",
      type: "UNKNOWN_TYPE",
      attributes: [],
    };

    const result = getTriggerClassInfo(trigger);

    expect(result).toBeNull();
  });
});
