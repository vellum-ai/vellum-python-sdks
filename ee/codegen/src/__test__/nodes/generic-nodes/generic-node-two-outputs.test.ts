import { v4 as uuidv4 } from "uuid";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { Writer } from "src/generators/extensions/writer";
import { GenericNode } from "src/generators/nodes/generic-node";

describe("GenericNode with two outputs", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: GenericNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory({ strict: false });
    writer = new Writer();
  });

  describe("generic node with list of strings and dict of string to VellumDocument outputs", () => {
    /**
     * Tests that a generic node with two outputs generates correctly:
     * - A list of strings (ARRAY type)
     * - A dictionary mapping strings to VellumDocument
     */
    it("getNodeFile", async () => {
      // GIVEN a generic node with two outputs
      const nodeData = genericNodeFactory({
        label: "TwoOutputsNode",
        nodeOutputs: [
          {
            id: uuidv4(),
            name: "string_list",
            type: "ARRAY",
            value: undefined,
          },
          {
            id: uuidv4(),
            name: "document_dict",
            type: "JSON",
            value: undefined,
            schema: {
              type: "object",
              additionalProperties: {
                $ref: "#/$defs/vellum.client.types.vellum_document.VellumDocument",
              },
            },
          },
        ],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      // WHEN we generate the node file
      node.getNodeFile().write(writer);

      // THEN the output should match the snapshot
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
