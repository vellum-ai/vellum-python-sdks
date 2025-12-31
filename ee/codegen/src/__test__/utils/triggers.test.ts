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
        { id: "attr-2", type: "STRING", key: "channel" },
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

  it("should return correct info for CHAT_MESSAGE trigger", () => {
    const trigger: WorkflowTrigger = {
      id: "chat-message-trigger-id",
      type: WorkflowTriggerType.CHAT_MESSAGE,
      attributes: [{ id: "attr-1", type: "JSON", key: "message" }],
    };

    const result = getTriggerClassInfo(trigger, workflowContextFactory());

    expect(result).toEqual({
      className: "ChatMessageTrigger",
      modulePath: ["code", "triggers", "chat_message"],
    });
  });

  it("should return correct info for CHAT_MESSAGE trigger with default attribute value", () => {
    const trigger: WorkflowTrigger = {
      id: "9e14c49b-c6d9-4fe5-9ff2-835fd695fe5f",
      type: WorkflowTriggerType.CHAT_MESSAGE,
      attributes: [
        {
          id: "5edbfd78-b634-4305-b2ad-d9feecbd5e5f",
          key: "message",
          type: "JSON",
          required: true,
          default: {
            type: "STRING",
            value: "Hello",
          },
          extensions: null,
          schema: null,
        },
      ],
      execConfig: {
        output: {
          type: "NODE_OUTPUT",
          nodeId: "6c43f557-304c-4f08-a8fd-13d1fb02d96a",
          nodeOutputId: "14f1265b-d5fb-4b60-b06b-9012029f6c6c",
        },
      },
      displayData: {
        label: "Chat Message",
        position: {
          x: 0.0,
          y: 0.0,
        },
        zIndex: 0,
        icon: "vellum:icon:message",
        color: "blue",
      },
    };

    const result = getTriggerClassInfo(trigger, workflowContextFactory());

    expect(result).toEqual({
      className: "ChatMessage",
      modulePath: ["code", "triggers", "chat_message"],
    });
  });
});
