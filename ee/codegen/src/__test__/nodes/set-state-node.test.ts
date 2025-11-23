import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import {
  genericNodeFactory,
  nodePortFactory,
  setStateNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { Writer } from "src/generators/extensions/writer";
import { GenericNode as GenericNodeClass } from "src/generators/nodes/generic-node";
import { NodePort } from "src/types/vellum";

describe("SetStateNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: GenericNodeClass;

  beforeEach(async () => {
    workflowContext = workflowContextFactory({ strict: false });
    writer = new Writer();

    // add a base node chat history output
    const chatHistoryNodeData = genericNodeFactory({
      id: "chat-history-node-id",
      nodeOutputs: [
        {
          id: "chat-history-node-output-id",
          name: "chat_history",
          type: "CHAT_HISTORY",
        },
      ],
    });
    await createNodeContext({
      workflowContext,
      nodeData: chatHistoryNodeData,
    });

    workflowContext.addStateVariableContext(
      stateVariableContextFactory({
        stateVariableData: {
          id: "state-counter-id",
          key: "counter",
          type: "NUMBER",
        },
        workflowContext,
      })
    );
    workflowContext.addStateVariableContext(
      stateVariableContextFactory({
        stateVariableData: {
          id: "state-chat-history-id",
          key: "chat_history",
          type: "CHAT_HISTORY",
        },
        workflowContext,
      })
    );
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodePortData: NodePort[] = [
        nodePortFactory({
          id: "set-state-port-id",
        }),
      ];
      const nodeData = setStateNodeFactory({ nodePorts: nodePortData });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNodeClass({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
