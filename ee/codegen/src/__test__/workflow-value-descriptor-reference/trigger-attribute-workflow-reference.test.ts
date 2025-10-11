import { Writer } from "@fern-api/python-ast/core/Writer";

import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { TriggerAttributeWorkflowReference } from "src/generators/workflow-value-descriptor-reference/trigger-attribute-workflow-reference";
import { WorkflowValueDescriptorReference } from "src/types/vellum";

describe("TriggerAttributeWorkflowReference", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory({
      triggers: [
        {
          id: "slack-trigger-id",
          type: "SLACK_MESSAGE",
          attributes: [
            { id: "message-id", name: "message" },
            { id: "user-id", name: "user" },
            { id: "channel-id", name: "channel" },
          ],
        },
      ],
    });
  });

  it("should generate correct AST for SlackTrigger.message reference", async () => {
    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "slack-trigger-id",
      attributeId: "message-id",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for SlackTrigger.user reference", async () => {
    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "slack-trigger-id",
      attributeId: "user-id",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should return undefined for non-existent trigger", async () => {
    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "non-existent-trigger",
      attributeId: "message-id",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    expect(pointer.getAstNode()).toBeUndefined();
  });

  it("should return undefined for non-existent attribute", async () => {
    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "slack-trigger-id",
      attributeId: "non-existent-attribute",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    expect(pointer.getAstNode()).toBeUndefined();
  });

  it("should handle ManualTrigger reference", async () => {
    const manualWorkflowContext = workflowContextFactory({
      triggers: [
        {
          id: "manual-trigger-id",
          type: "MANUAL",
          attributes: [{ id: "input-id", name: "input" }],
        },
      ],
    });

    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "manual-trigger-id",
      attributeId: "input-id",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext: manualWorkflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
