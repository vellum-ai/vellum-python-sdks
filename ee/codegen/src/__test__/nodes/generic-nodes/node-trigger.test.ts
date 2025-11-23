import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { Writer } from "src/generators/extensions/writer";
import { NodeTrigger } from "src/generators/node-trigger";
import { NodeTrigger as NodeTriggerType } from "src/types/vellum";

describe("NodeTrigger", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let nodeTrigger: NodeTrigger;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodeTriggerData: NodeTriggerType = {
        id: "some-id",
        mergeBehavior: "AWAIT_ALL",
      };
      const nodeData = genericNodeFactory({
        label: "MyGenericNode",
        nodeTrigger: nodeTriggerData,
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      nodeTrigger = new NodeTrigger({
        nodeTrigger: nodeTriggerData,
        nodeContext,
      });
    });

    it("generates correct trigger class", async () => {
      nodeTrigger.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
