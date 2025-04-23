import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import {
  retryAdornmentFactory,
  templatingNodeFactory,
  tryAdornmentFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { TemplatingNode } from "src/generators/nodes/templating-node";
import { AdornmentNode } from "src/types/vellum";

describe("Adorned Node", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: TemplatingNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("try adornment no error code", () => {
    beforeEach(async () => {
      const adornments: AdornmentNode[] = [tryAdornmentFactory()];
      const nodeData = templatingNodeFactory()
        .withAdornments(adornments)
        .build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("try adornment with error code", () => {
    beforeEach(async () => {
      const adornments: AdornmentNode[] = [
        tryAdornmentFactory({ errorCode: "INVALID_CODE" }),
      ];
      const nodeData = templatingNodeFactory()
        .withAdornments(adornments)
        .build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("Retry adornment no error code", () => {
    beforeEach(async () => {
      const adornments: AdornmentNode[] = [retryAdornmentFactory()];
      const nodeData = templatingNodeFactory()
        .withAdornments(adornments)
        .build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("retry adornment with error code and max attempts and delay", () => {
    beforeEach(async () => {
      const adornments: AdornmentNode[] = [
        retryAdornmentFactory({
          errorCode: "INVALID_CODE",
          maxAttempts: 5,
          delay: 2.5,
        }),
      ];
      const nodeData = templatingNodeFactory()
        .withAdornments(adornments)
        .build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
