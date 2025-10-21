import { describe, it, expect } from "vitest";

import { WorkflowTrigger, WorkflowTriggerType } from "src/types/vellum";
import { getTriggerClassInfo } from "src/utils/triggers";

describe("getTriggerClassInfo", () => {
  it("should return correct info for MANUAL trigger", () => {
    const trigger: WorkflowTrigger = {
      id: "manual-trigger-id",
      type: WorkflowTriggerType.MANUAL,
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
      type: WorkflowTriggerType.INTEGRATION,
      attributes: [
        { id: "attr-1", name: "message", value: null },
        { id: "attr-2", name: "channel", value: null },
      ],
      className: "SlackMessageTrigger",
      modulePath: ["tests", "fixtures", "triggers", "slack_message"],
    };

    const result = getTriggerClassInfo(trigger);

    expect(result).toEqual({
      className: "SlackMessageTrigger",
      modulePath: ["tests", "fixtures", "triggers", "slack_message"],
    });
  });
});
