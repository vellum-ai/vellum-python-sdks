import { describe, it, expect } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers/workflow-context-factory";
import {
  IntegrationProvider,
  WorkflowTrigger,
  WorkflowTriggerType,
} from "src/types/vellum";
import { getTriggerClassInfo } from "src/utils/triggers";

describe("getTriggerClassInfo", () => {
  it("should return correct info for MANUAL trigger", () => {
    const trigger: WorkflowTrigger = {
      id: "manual-trigger-id",
      type: WorkflowTriggerType.MANUAL,
      attributes: [],
    };

    const result = getTriggerClassInfo(trigger, workflowContextFactory());

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
      cron: "* * * * *",
      timezone: "UTC",
    };

    const result = getTriggerClassInfo(trigger, workflowContextFactory());

    expect(result).toEqual({
      className: "ScheduleTrigger",
      modulePath: ["code", "triggers", "scheduled"],
    });
  });

  it("should return correct info for INTEGRATION trigger", () => {
    const trigger: WorkflowTrigger = {
      id: "integration-trigger-id",
      type: WorkflowTriggerType.INTEGRATION,
      attributes: [
        { id: "attr-1", type: "STRING", key: "message" },
        { id: "attr-2", type: "STRING", key: "channel"},
      ],
      execConfig: {
        type: IntegrationProvider.COMPOSIO,
        slug: "SLACK_NEW_MESSAGE",
        setupAttributes: [],
        integrationName: "slack",
      },
    };

    const result = getTriggerClassInfo(
      trigger,
      workflowContextFactory({
        moduleName: "tests.fixtures",
      })
    );

    expect(result).toEqual({
      className: "SlackNewMessage",
      modulePath: ["tests", "fixtures", "triggers", "slack_new_message"],
    });
  });
});
