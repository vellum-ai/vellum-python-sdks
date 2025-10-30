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

  it("should return correct info for SCHEDULED trigger", () => {
    const trigger: WorkflowTrigger = {
      id: "scheduled-trigger-id",
      type: WorkflowTriggerType.SCHEDULED,
      attributes: [],
      cron: "0 0 * * *",
      timezone: "America/New_York",
      nextRunAt: "2024-01-01T00:00:00Z",
    };

    const result = getTriggerClassInfo(trigger);

    expect(result).toEqual({
      className: "ScheduleTrigger",
      modulePath: ["vellum", "workflows", "triggers", "scheduled"],
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
      execConfig: {
        type: "COMPOSIO" as const,
        slug: "SLACK_NEW_MESSAGE",
        setupAttributes: [],
        integrationName: "slack",
      },
      className: "SlackMessageTrigger",
      modulePath: ["tests", "fixtures", "triggers", "slack_message"],
      sourceHandleId: "integration-trigger-id",
    };

    const result = getTriggerClassInfo(trigger);

    expect(result).toEqual({
      className: "SlackMessageTrigger",
      modulePath: ["tests", "fixtures", "triggers", "slack_message"],
    });
  });
});
