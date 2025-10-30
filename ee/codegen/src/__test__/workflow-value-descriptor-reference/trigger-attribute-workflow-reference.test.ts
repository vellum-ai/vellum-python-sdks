import { Writer } from "@fern-api/python-ast/core/Writer";

import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { TriggerAttributeWorkflowReference } from "src/generators/workflow-value-descriptor-reference/trigger-attribute-workflow-reference";
import {
  WorkflowValueDescriptorReference,
  WorkflowTriggerType,
} from "src/types/vellum";

describe("TriggerAttributeWorkflowReference", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory({
      triggers: [
        {
          id: "manual-trigger-id",
          type: WorkflowTriggerType.MANUAL,
          attributes: [
            { id: "input-id", name: "input" },
            { id: "config-id", name: "config" },
          ],
        },
      ],
    });
  });

  it("should generate correct AST for ManualTrigger.input reference", async () => {
    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "manual-trigger-id",
      attributeId: "input-id",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for ManualTrigger.config reference", async () => {
    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "manual-trigger-id",
      attributeId: "config-id",
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
      attributeId: "input-id",
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
      triggerId: "manual-trigger-id",
      attributeId: "non-existent-attribute",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    expect(pointer.getAstNode()).toBeUndefined();
  });

  it("should generate correct AST for IntegrationTrigger.message reference", async () => {
    const integrationWorkflowContext = workflowContextFactory({
      triggers: [
        {
          id: "integration-trigger-id",
          type: WorkflowTriggerType.INTEGRATION,
          attributes: [
            { id: "message-id", name: "message", value: null },
            { id: "channel-id", name: "channel", value: null },
          ],
          className: "SlackMessageTrigger",
          modulePath: ["tests", "fixtures", "triggers", "slack_message"],
          sourceHandleId: "integration-trigger-id",
        },
      ],
    });

    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "integration-trigger-id",
      attributeId: "message-id",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext: integrationWorkflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for IntegrationTrigger.channel reference", async () => {
    const integrationWorkflowContext = workflowContextFactory({
      triggers: [
        {
          id: "integration-trigger-id",
          type: WorkflowTriggerType.INTEGRATION,
          attributes: [
            { id: "message-id", name: "message", value: null },
            { id: "channel-id", name: "channel", value: null },
          ],
          className: "SlackMessageTrigger",
          modulePath: ["tests", "fixtures", "triggers", "slack_message"],
          sourceHandleId: "integration-trigger-id",
        },
      ],
    });

    const triggerAttributeReference: WorkflowValueDescriptorReference = {
      type: "TRIGGER_ATTRIBUTE",
      triggerId: "integration-trigger-id",
      attributeId: "channel-id",
    };

    const pointer = new TriggerAttributeWorkflowReference({
      workflowContext: integrationWorkflowContext,
      nodeInputWorkflowReferencePointer: triggerAttributeReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
