import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";

import { workflowContextFactory } from "./helpers";
import {
  EdgeFactoryNodePair,
  edgesFactory,
} from "./helpers/edge-data-factories";
import {
  conditionalNodeFactory,
  entrypointNodeDataFactory,
  finalOutputNodeFactory,
  genericNodeFactory,
  mergeNodeDataFactory,
  nodePortFactory,
  nodePortsFactory,
  templatingNodeFactory,
} from "./helpers/node-data-factories";

import { createNodeContext } from "src/context";
import { GraphAttribute } from "src/generators/graph-attribute";
import { WorkflowTriggerType } from "src/types/vellum";

describe("Workflow", () => {
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

  describe("graph", () => {
    it("should be correct for a basic single node case", async () => {
      const templatingNodeData = templatingNodeFactory().build();

      await runGraphTest([[entrypointNode, templatingNodeData]]);
    });

    it("should be correct for a basic multiple nodes case", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
      ]);
    });

    it("should be correct for three nodes", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [entrypointNode, templatingNodeData3],
      ]);
    });

    it("should be correct for a basic single edge case", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
      ]);
    });

    it("should be correct for a basic merge node case", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const mergeNodeData = mergeNodeDataFactory().build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [templatingNodeData1, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
      ]);
    });

    it("should be correct for a basic merge node case of multiple nodes", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const mergeNodeData = mergeNodeDataFactory(3).build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [entrypointNode, templatingNodeData3],
        [templatingNodeData1, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
        [templatingNodeData3, [mergeNodeData, 2]],
      ]);
    });

    it("should be correct for a basic merge node and an additional edge", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const mergeNodeData = mergeNodeDataFactory().build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [templatingNodeData1, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
        [mergeNodeData, templatingNodeData3],
      ]);
    });

    it("should be correct for a basic merge between a node and an edge", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const mergeNodeData = mergeNodeDataFactory().build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
        [templatingNodeData2, [mergeNodeData, 0]],
        [templatingNodeData3, [mergeNodeData, 1]],
      ]);
    });

    it("should be correct for a basic conditional node case", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const conditionalNodeData = conditionalNodeFactory().build();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "1"], templatingNodeData2],
      ]);
    });

    it("should be correct for a longer branch", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
        [templatingNodeData2, templatingNodeData3],
      ]);
    });

    it("should be correct for set of a branch and a node", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
        [entrypointNode, templatingNodeData3],
      ]);
    });

    it("should be correct for a node to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
      ]);
    });

    it("should be correct for a node to a set to a node", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
        [templatingNodeData3, templatingNodeData4],
        [templatingNodeData2, templatingNodeData4],
      ]);
    });

    it("should be correct for set of a branch and a node to a node", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData5 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 5",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const mergeNodeData = mergeNodeDataFactory().build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
        [templatingNodeData3, templatingNodeData4],
        [templatingNodeData4, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
        [mergeNodeData, templatingNodeData5],
      ]);
    });

    it("should be correct for a single port pointing to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const conditionalNodeData = conditionalNodeFactory().build();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "0"], templatingNodeData2],
      ]);
    });

    it("should be correct for port within set to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const conditionalNodeData = conditionalNodeFactory().build();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "1"], templatingNodeData2],
        [[conditionalNodeData, "1"], templatingNodeData3],
      ]);
    });

    it("should be correct for a nested conditional node within a set", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const conditionalNodeData = conditionalNodeFactory().build();

      const conditionalNode2Data = conditionalNodeFactory({
        id: uuidv4(),
        label: "Conditional Node 2",
        targetHandleId: uuidv4(),
        ifSourceHandleId: uuidv4(),
        elseSourceHandleId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "1"], conditionalNode2Data],
        [[conditionalNodeData, "1"], templatingNodeData2],
        [[conditionalNode2Data, "1"], templatingNodeData3],
        [[conditionalNode2Data, "1"], templatingNodeData4],
      ]);
    });

    it("should be correct for two branches merging from sets", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const templatingNodeData5 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 5",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const conditionalNodeData = conditionalNodeFactory().build();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "1"], templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
        [templatingNodeData2, templatingNodeData3],
        [templatingNodeData3, templatingNodeData4],
        [templatingNodeData1, templatingNodeData5],
      ]);
    });

    it("should be correct for two branches from the same node", async () => {
      const templatingNodeData1 = templatingNodeFactory().build();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const mergeNodeData = mergeNodeDataFactory().build();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
        [templatingNodeData1, templatingNodeData2],
      ]);
    });

    it("should define nested sets of nodes without compilation errors", async () => {
      const topNode = templatingNodeFactory({ label: "Top Node" }).build();

      const outputTopNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Output Top Node",
        name: "output-top-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      }).build();

      const outputMiddleNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Output Middle Node",
        name: "output-middle-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      }).build();

      const outputBottomNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Output Bottom Node",
        name: "output-bottom-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      }).build();

      await runGraphTest([
        [entrypointNode, topNode],
        [topNode, outputTopNode],
        [topNode, outputMiddleNode],
        [topNode, outputBottomNode],
      ]);
    });

    it("should support an edge between two sets", async () => {
      const topLeftNode = templatingNodeFactory({
        label: "Top Left Node",
      }).build();

      const topRightNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Top Right Node",
        name: "top-right-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      }).build();

      const bottomLeftNode = templatingNodeFactory({
        id: uuidv4(),
        label: "Bottom Left Node",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const bottomRightNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Bottom Right Node",
        name: "bottom-right-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      }).build();

      /**
       * Currently the snapshot generated for this test is suboptimal. Ideally, we would generate:
       *
       * {
       *     TopLeftNode,
       *     BottomLeftNode,
       * } >> Graph.from_set(
       *     {
       *         TopRightNode,
       *         BottomRightNode,
       *     }
       * )
       */
      await runGraphTest([
        [entrypointNode, topLeftNode],
        [entrypointNode, bottomLeftNode],
        [topLeftNode, topRightNode],
        [bottomLeftNode, topRightNode],
        [topLeftNode, bottomRightNode],
        [bottomLeftNode, bottomRightNode],
      ]);
    });

    it("should handle a simple edge of generic nodes", async () => {
      const startNode = genericNodeFactory({
        label: "StartNode",
      });

      const endNode = genericNodeFactory({
        label: "EndNode",
      });

      await runGraphTest([
        [entrypointNode, startNode],
        [startNode, endNode],
      ]);
    });

    it("should be pointing to the correct terminal nodes from a nested set of conditionals", async () => {
      const firstCheckNode = genericNodeFactory({
        label: "FirstCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const firstInnerCheckNode = genericNodeFactory({
        label: "FirstInnerCheckNode",
      });

      const finalCheckNode = genericNodeFactory({
        label: "FinalCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const innerTerminalNode = genericNodeFactory({
        label: "InnerTerminalNode",
      });

      const secondInnerCheckNode = genericNodeFactory({
        label: "SecondInnerCheckNode",
      });

      const outerOutputNode = genericNodeFactory({
        label: "OuterOutputNode",
      });

      await runGraphTest([
        [entrypointNode, firstCheckNode],
        [[firstCheckNode, "if_port"], firstInnerCheckNode],
        [[firstCheckNode, "else_port"], finalCheckNode],
        [firstInnerCheckNode, secondInnerCheckNode],
        [[finalCheckNode, "if_port"], innerTerminalNode],
        [[finalCheckNode, "else_port"], outerOutputNode],
        [secondInnerCheckNode, finalCheckNode],
      ]);
    });

    it.skip("should be able to create a proper else edge when there are three ports pointing to a set", async () => {
      const firstCheckNode = genericNodeFactory({
        label: "FirstCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const firstInnerCheckNode = genericNodeFactory({
        label: "FirstInnerCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const finalCheckNode = genericNodeFactory({
        label: "FinalCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const innerTerminalNode = genericNodeFactory({
        label: "InnerTerminalNode",
      });

      const secondInnerCheckNode = genericNodeFactory({
        label: "SecondInnerCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const outerOutputNode = genericNodeFactory({
        label: "OuterOutputNode",
      });

      await runGraphTest([
        [entrypointNode, firstCheckNode],
        [[firstCheckNode, "if_port"], firstInnerCheckNode],
        [[firstCheckNode, "else_port"], finalCheckNode],
        [[firstInnerCheckNode, "if_port"], secondInnerCheckNode],
        [[firstInnerCheckNode, "else_port"], finalCheckNode],
        [[finalCheckNode, "if_port"], innerTerminalNode],
        [[finalCheckNode, "else_port"], outerOutputNode],
        [[secondInnerCheckNode, "if_port"], finalCheckNode],
        [[secondInnerCheckNode, "else_port"], outerOutputNode],
      ]);
      /**
       * Currently creating the following incorrect graph:
{
    FirstCheckNode.Ports.if_port
    >> {
        FirstInnerCheckNode.Ports.if_port >> SecondInnerCheckNode.Ports.if_port,
        FirstInnerCheckNode.Ports.else_port,
    },
    FirstCheckNode.Ports.else_port,
} >> Graph.from_set(
    {
        FinalCheckNode.Ports.if_port >> InnerTerminalNode,
        FinalCheckNode.Ports.else_port >> OuterOutputNode,
        OuterOutputNode,
    }
)
        * This graph incorrectly adds `OuterOutputNode` to the right hand side set, instead of
        * creating the proper `else` edge for `SecondInnerCheckNode`.
        */
    });

    it("Should handle an else case within a conditioned set", async () => {
      const firstCheckNode = genericNodeFactory({
        label: "FirstCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const firstOutputNode = genericNodeFactory({
        label: "FirstOutputNode",
      });

      const secondCheckNode = genericNodeFactory({
        label: "SecondInnerCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const secondOutputNode = genericNodeFactory({
        label: "SecondOutputNode",
      });

      /**
       * This snapshot is not optimal. Ideally, we would generate:
{
    FirstCheckNode.Ports.if_port >> {
        SecondInnerCheckNode.Ports.if_port >> FirstOutputNode,
        SecondInnerCheckNode.Ports.else_port >> SecondOutputNode,
    },
    FirstCheckNode.Ports.else_port >> FirstOutputNode,
}
       */
      await runGraphTest([
        [entrypointNode, firstCheckNode],
        [[firstCheckNode, "if_port"], secondCheckNode],
        [[firstCheckNode, "else_port"], firstOutputNode],
        [[secondCheckNode, "if_port"], firstOutputNode],
        [[secondCheckNode, "else_port"], secondOutputNode],
      ]);
    });

    it("Should handle an a conditional pointing both ports to the same conditional node", async () => {
      const firstCheckNode = genericNodeFactory({
        label: "FirstCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const firstOutputNode = genericNodeFactory({
        label: "FirstOutputNode",
      });

      const secondCheckNode = genericNodeFactory({
        label: "SecondCheckNode",
        nodePorts: nodePortsFactory(),
      });

      const secondOutputNode = genericNodeFactory({
        label: "SecondOutputNode",
      });

      const thirdOutputNode = genericNodeFactory({
        label: "ThirdOutputNode",
      });

      const fourthOutputNode = genericNodeFactory({
        label: "FourthOutputNode",
      });

      await runGraphTest([
        [entrypointNode, firstCheckNode],
        [[firstCheckNode, "if_port"], secondCheckNode],
        [[firstCheckNode, "else_port"], firstOutputNode],
        [firstOutputNode, secondCheckNode],
        [[secondCheckNode, "if_port"], secondOutputNode],
        [[secondCheckNode, "else_port"], thirdOutputNode],
        [secondOutputNode, fourthOutputNode],
        [thirdOutputNode, fourthOutputNode],
      ]);
    });

    it("Should handle two branches from a node to a node", async () => {
      const firstNode = genericNodeFactory({
        label: "FirstNode",
      });

      const secondNode = genericNodeFactory({
        label: "SecondNode",
      });

      const thirdNode = genericNodeFactory({
        label: "ThirdNode",
      });

      const fourthNode = genericNodeFactory({
        label: "FourthNode",
      });

      const fifthNode = genericNodeFactory({
        label: "FifthNode",
        nodePorts: nodePortsFactory(),
      });

      await runGraphTest([
        [entrypointNode, firstNode],
        [firstNode, secondNode],
        [firstNode, fourthNode],
        [secondNode, thirdNode],
        [thirdNode, fourthNode],
        [fourthNode, fifthNode],
      ]);
    });

    it("Should solve a case with a branched node within a set into a merge node", async () => {
      const EntrypointNode = entrypointNodeDataFactory();

      const StartNode = genericNodeFactory({
        label: "StartNode",
      });

      const TopNode = genericNodeFactory({
        label: "TopNode",
      });

      const BottomNode = genericNodeFactory({
        label: "BottomNode",
      });

      const SecondBottomNode = genericNodeFactory({
        label: "SecondBottomNode",
      });

      const MergeNode = genericNodeFactory({
        label: "MergeNode",
      });

      await runGraphTest([
        [EntrypointNode, StartNode],
        [StartNode, TopNode],
        [StartNode, BottomNode],
        [TopNode, MergeNode],
        [BottomNode, MergeNode],
        [SecondBottomNode, MergeNode],
        [BottomNode, SecondBottomNode],
      ]);
    });
    it("should properly format UUID-like port names in graph references", async () => {
      // Given a UUID-like port names
      const uuidPortName1 = "7d813792-04c2-4d26-a126-16de4c4cebaf";
      const uuidPortName2 = "6f909cc6-887c-46d8-966b-46547900fc9c";

      const genericNodeData = genericNodeFactory({
        label: "GenericNode",
        nodePorts: [
          {
            id: uuidv4(),
            name: uuidPortName1,
            type: "IF",
            expression: {
              type: "CONSTANT_VALUE",
              value: { type: "STRING", value: "test" },
            },
          },
          {
            id: uuidv4(),
            name: uuidPortName2,
            type: "ELSE",
          },
        ],
      });

      const firstNode = genericNodeFactory({
        label: "FirstNode",
      });

      const secondNode = genericNodeFactory({
        label: "SecondNode",
      });

      await runGraphTest([
        [entrypointNode, genericNodeData],
        [[genericNodeData, uuidPortName1], firstNode],
        [[genericNodeData, uuidPortName2], secondNode],
      ]);
    });

    it("should generate correct graph for a loop with ports", async () => {
      const EntrypointNode = entrypointNodeDataFactory();

      const ifPortId = "583edca2-29ff-4462-8859-72c07159b777";
      const elsePortId = "09e71028-e2b1-4a63-a929-f72414351ac6";

      const genericNodeId = "9211255a-f1c7-4211-869f-a0ed344bb2fd";

      const FirstNode = genericNodeFactory({
        id: genericNodeId,
        label: "FirstNode",
        nodePorts: [
          nodePortFactory({
            type: "IF",
            id: ifPortId,
            expression: {
              type: "BINARY_EXPRESSION",
              operator: "=",
              lhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "Hi",
                },
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "Some value",
                },
              },
            },
          }),
          nodePortFactory({
            type: "ELSE",
            id: elsePortId,
          }),
        ],
      });

      const SecondNode = genericNodeFactory({
        id: "971ae206-1467-42e1-b5fc-60f44727a6bd",
        label: "SecondNode",
      });

      const FinalNode = finalOutputNodeFactory({
        label: "FinalNode",
      }).build();

      await runGraphTest([
        [EntrypointNode, FirstNode],
        [SecondNode, FirstNode],
        [[FirstNode, "if_port"], FinalNode],
        [[FirstNode, "else_port"], SecondNode],
      ]);
    });

    it("should generate correct graph for expression reference own output", async () => {
      const EntrypointNode = entrypointNodeDataFactory();

      const ifPortId = "583edca2-29ff-4462-8859-72c07159b777";
      const elsePortId = "09e71028-e2b1-4a63-a929-f72414351ac6";

      const PromptNode = genericNodeFactory({
        id: "inline-prompt-node",
        label: "Prompt",
        nodePorts: [
          nodePortFactory({
            type: "IF",
            id: ifPortId,
            name: "group_1_if_port",
            expression: {
              type: "BINARY_EXPRESSION",
              operator: "=",
              lhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "Hi",
                },
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "Some value",
                },
              },
            },
          }),
          nodePortFactory({
            type: "ELSE",
            id: elsePortId,
            name: "group_1_else_port",
          }),
        ],
      });

      const SecondNode = genericNodeFactory({
        id: "second-node",
        label: "SecondNode",
      });

      const FinalOutput = finalOutputNodeFactory({
        id: "final-output-node",
        label: "FinalOutput",
      }).build();

      await runGraphTest([
        [EntrypointNode, PromptNode],
        [[PromptNode, "group_1_if_port"], FinalOutput],
        [[PromptNode, "group_1_else_port"], SecondNode],
        [SecondNode, PromptNode],
      ]);
    });

    it("should generate correct graph when workflow has a manual trigger", async () => {
      const writer = new Writer();

      const triggerId = "trigger-1";

      const firstNode = genericNodeFactory({
        id: "first-node",
        label: "FirstNode",
      });

      const secondNode = genericNodeFactory({
        id: "second-node",
        label: "SecondNode",
      });

      // When a trigger is present, it IS the entry point - no entrypoint node needed
      const edges = edgesFactory([[firstNode, secondNode]]);

      const workflowContext = workflowContextFactory({
        workflowRawData: {
          nodes: [firstNode, secondNode],
          edges,
        },
        triggers: [
          {
            id: triggerId,
            type: WorkflowTriggerType.MANUAL,
            attributes: [],
          },
        ],
      });

      await Promise.all([
        createNodeContext({
          nodeData: firstNode,
          workflowContext,
        }),
        createNodeContext({
          nodeData: secondNode,
          workflowContext,
        }),
      ]);

      const graphAttribute = new GraphAttribute({
        workflowContext,
      });

      graphAttribute.write(writer);

      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct graph when workflow has a VellumIntegrationTrigger", async () => {
      const writer = new Writer();

      const triggerId = "trigger-1";

      const firstNode = genericNodeFactory({
        id: "first-node",
        label: "FirstNode",
      });

      const secondNode = genericNodeFactory({
        id: "second-node",
        label: "SecondNode",
      });

      // When a trigger is present, it IS the entry point - no entrypoint node needed
      const edges = edgesFactory([[firstNode, secondNode]]);

      const workflowContext = workflowContextFactory({
        workflowRawData: {
          nodes: [firstNode, secondNode],
          edges,
        },
        triggers: [
          {
            id: triggerId,
            type: WorkflowTriggerType.INTEGRATION,
            attributes: [
              { id: "attr-1", name: "message", value: null },
              { id: "attr-2", name: "channel", value: null },
            ],
            className: "SlackMessageTrigger",
            modulePath: ["tests", "fixtures", "triggers", "slack_message"],
            sourceHandleId: triggerId, // Use trigger ID as handle ID
          },
        ],
      });

      await Promise.all([
        createNodeContext({
          nodeData: firstNode,
          workflowContext,
        }),
        createNodeContext({
          nodeData: secondNode,
          workflowContext,
        }),
      ]);

      const graphAttribute = new GraphAttribute({
        workflowContext,
      });

      graphAttribute.write(writer);

      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle a conditional node with default port pointing back to itself", async () => {
      const validateAPIResponseNode = genericNodeFactory({
        id: uuidv4(),
        label: "ValidateAPIResponse",
        nodePorts: [
          nodePortFactory({ name: "success", type: "IF" }),
          nodePortFactory({ name: "network_error", type: "IF" }),
          nodePortFactory({ name: "api_error", type: "IF" }),
          nodePortFactory({ name: "default", type: "ELSE" }),
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
        [[validateAPIResponseNode, "default"], validateAPIResponseNode],
      ]);
    });
  });
});
