import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodePorts } from "src/generators/node-port";
import { NodePort } from "src/types/vellum";

describe("NodePorts", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let nodePorts: NodePorts;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodePortsData: NodePort[] = [
        {
          type: "IF",
          id: "port-2",
          name: "if_port",
          expression: {
            type: "CONSTANT_VALUE",
            data: {
              type: "STRING",
              value: "test",
            },
          },
        },
        {
          type: "ELSE",
          id: "port-3",
          name: "else_port",
        },
      ];

      const nodeData = genericNodeFactory({
        name: "MyGenericNode",
        nodePorts: nodePortsData,
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;
      workflowContext.addNodeContext(nodeContext);

      nodePorts = new NodePorts({
        nodePorts: nodePortsData,
        nodeContext,
        workflowContext,
      });
    });

    it("generates correct ports class", async () => {
      nodePorts.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
