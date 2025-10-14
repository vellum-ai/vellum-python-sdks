import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";

import { workflowContextFactory } from "./helpers";
import {
  EdgeFactoryNodePair,
  edgesFactory,
} from "./helpers/edge-data-factories";
import {
  entrypointNodeDataFactory,
  finalOutputNodeFactory,
  genericNodeFactory,
  nodePortFactory,
} from "./helpers/node-data-factories";

import { createNodeContext } from "src/context";
import { GraphAttribute } from "src/generators/graph-attribute";

describe("Graph", () => {
  const entrypointNode = entrypointNodeDataFactory();
  const runGraphTest = async (edgeFactoryNodePairs: EdgeFactoryNodePair[]) => {
    const writer = new Writer();

    const nodes = Array.from(
      new Set(
        edgeFactoryNodePairs.flatMap(([source, target]) => [
          Array.isArray(source) ? source[0] : source,
          Array.isArray(target) ? target[0] : target,
        ])
      )
    );
    const edges = edgesFactory(edgeFactoryNodePairs);

    const workflowContext = workflowContextFactory({
      workflowRawData: {
        nodes,
        edges,
      },
    });

    await Promise.all(
      nodes.map((node) => {
        if (node.type === "ENTRYPOINT") {
          return;
        }

        createNodeContext({
          workflowContext,
          nodeData: node,
        });
      })
    );

    new GraphAttribute({ workflowContext }).write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  };

  describe("self-referencing else port", () => {
    it("should handle a conditional node with else port pointing back to itself", async () => {
      /**
       * Reproduces the issue from APO-1882 where a self-referencing else port
       * generates an invalid graph structure.
       *
       * The expected graph should be:
       * {
       *     ValidateAPIResponse.Ports.success >> APISuccessOutput,
       *     {
       *         ValidateAPIResponse.Ports.network_error,
       *         ValidateAPIResponse.Ports.api_error,
       *     } >> APIErrorHandler,
       *     ValidateAPIResponse.Ports.else_port >> ValidateAPIResponse,
       * }
       */
      const validateAPIResponseNode = genericNodeFactory({
        id: uuidv4(),
        label: "ValidateAPIResponse",
        nodePorts: [
          nodePortFactory({ name: "success" }),
          nodePortFactory({ name: "network_error" }),
          nodePortFactory({ name: "api_error" }),
          nodePortFactory({ name: "else_port", type: "ELSE" }),
        ],
      });

      const apiSuccessOutputNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "APISuccessOutput",
        name: "api_success_output",
      }).build();

      const apiErrorHandlerNode = genericNodeFactory({
        id: uuidv4(),
        label: "APIErrorHandler",
      });

      await runGraphTest([
        [entrypointNode, validateAPIResponseNode],
        [[validateAPIResponseNode, "success"], apiSuccessOutputNode],
        [[validateAPIResponseNode, "network_error"], apiErrorHandlerNode],
        [[validateAPIResponseNode, "api_error"], apiErrorHandlerNode],
        [[validateAPIResponseNode, "else_port"], validateAPIResponseNode],
      ]);

    });
  });
});
