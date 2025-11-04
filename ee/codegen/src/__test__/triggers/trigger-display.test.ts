import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { IntegrationTrigger } from "src/generators/triggers/integration-trigger";
import type { IntegrationTrigger as IntegrationTriggerType } from "src/types/vellum";

describe("TriggerDisplay", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
  });

  it.each([
    {
      name: "with icon and color",
      displayData: {
        label: "My Trigger",
        icon: "🎨",
        color: "#FF5733"
      },
    },
    {
      name: "with only icon",
      displayData: {
        label: "My Trigger",
        icon: "🔧"
      },
    },
    {
      name: "with only color",
      displayData: {
        label: "My Trigger",
        color: "#00FF00"
      },
    },
    {
      name: "without icon or color",
      displayData: {
        label: "My Trigger",
        position: { x: 100, y: 200 }
      },
    },
    {
      name: "with null icon and color",
      displayData: {
        label: "My Trigger",
        icon: null,
        color: null
      },
    },
  ])("$name", async ({ displayData }) => {
    /**
     * Tests that the TriggerDisplay generator correctly generates Display classes
     * for triggers with various combinations of icon and color attributes.
     */

    const triggerData: IntegrationTriggerType = {
      id: "test-trigger-id",
      type: "INTEGRATION",
      execConfig: {
        type: "COMPOSIO",
        integrationName: "slack",
        slug: "my_custom_trigger",
        setupAttributes: [],
      },
      attributes: [
        {
          id: "attr-1",
          name: "message",
          value: null,
        },
      ],
      displayData: displayData,
    };

    const trigger = new IntegrationTrigger({
      workflowContext,
      trigger: triggerData,
    });
    const triggerStatements = trigger.getFileStatements();
    const triggerClass = triggerStatements[0];

    const writer = new Writer();
    triggerClass.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
