import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { Writer } from "src/generators/extensions/writer";
import { TriggerAttributePointerRule } from "src/generators/node-inputs";

describe("TriggerAttributePointer", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should generate correct Python code for trigger attribute reference", async () => {
    /**
     * Tests that TriggerAttributePointer generates the correct Python reference
     * to a trigger's attribute (e.g., SlackTrigger.channel_id)
     */

    // GIVEN a workflow context with an integration trigger
    const workflowContext = workflowContextFactory();
    workflowContext.triggers = [
      {
        id: "slack-trigger-id",
        type: "INTEGRATION",
        execConfig: {
          type: "COMPOSIO",
          integrationName: "SLACK",
          slug: "SLACK_NEW_MESSAGE_TRIGGER",
          setupAttributes: [],
        },
        attributes: [
          {
            id: "channel-id-attribute",
            key: "channel_id",
            type: "STRING",
          },
          {
            id: "message-attribute",
            key: "message",
            type: "STRING",
          },
        ],
        displayData: {
          label: "Slack New Message Trigger",
          position: { x: 100, y: 200 },
          zIndex: 1,
          icon: "slack",
          color: "#4A154B",
        },
      },
    ];

    // AND a node context
    const nodeContext = await nodeContextFactory({ workflowContext });

    // WHEN we create a TriggerAttributePointerRule for the channel_id attribute
    const triggerAttributePointer = new TriggerAttributePointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "TRIGGER_ATTRIBUTE",
        data: {
          triggerId: "slack-trigger-id",
          attributeId: "channel-id-attribute",
        },
      },
    });

    // AND write it to the writer
    triggerAttributePointer.write(writer);

    // THEN the generated code should reference the trigger class and attribute
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle when trigger does not exist", async () => {
    /**
     * Tests that TriggerAttributePointer handles missing triggers gracefully
     * by returning None in non-strict mode
     */

    // GIVEN a workflow context with no triggers
    const workflowContext = workflowContextFactory({ strict: false });
    const nodeContext = await nodeContextFactory({ workflowContext });

    // WHEN we create a TriggerAttributePointerRule for a non-existent trigger
    const triggerAttributePointer = new TriggerAttributePointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "TRIGGER_ATTRIBUTE",
        data: {
          triggerId: "missing-trigger-id",
          attributeId: "some-attribute-id",
        },
      },
    });

    // AND write it to the writer
    triggerAttributePointer.write(writer);

    // THEN the generated code should return None
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle when attribute does not exist on trigger", async () => {
    /**
     * Tests that TriggerAttributePointer handles missing attributes gracefully
     * by returning None in non-strict mode
     */

    // GIVEN a workflow context with a trigger that has specific attributes
    const workflowContext = workflowContextFactory({ strict: false });
    workflowContext.triggers = [
      {
        id: "linear-trigger-id",
        type: "INTEGRATION",
        execConfig: {
          type: "COMPOSIO",
          integrationName: "LINEAR",
          slug: "LINEAR_COMMENT_EVENT_TRIGGER",
          setupAttributes: [],
        },
        attributes: [
          {
            id: "action-attribute-id",
            key: "action",
            type: "STRING",
          },
        ],
        displayData: {
          label: "Linear Comment Event Trigger",
          position: { x: 100, y: 200 },
          zIndex: 1,
          icon: "linear",
          color: "#5E6AD2",
        },
      },
    ];

    // AND a node context
    const nodeContext = await nodeContextFactory({ workflowContext });

    // WHEN we create a TriggerAttributePointerRule for a non-existent attribute
    const triggerAttributePointer = new TriggerAttributePointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "TRIGGER_ATTRIBUTE",
        data: {
          triggerId: "linear-trigger-id",
          attributeId: "missing-attribute-id",
        },
      },
    });

    // AND write it to the writer
    triggerAttributePointer.write(writer);

    // THEN the generated code should return None
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
