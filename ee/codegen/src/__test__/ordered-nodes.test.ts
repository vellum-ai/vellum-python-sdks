import { workflowContextFactory } from "./helpers";
import {
  EdgeFactoryNodePair,
  edgesFactory,
} from "./helpers/edge-data-factories";
import {
  entrypointNodeDataFactory,
  genericNodeFactory,
  mergeNodeDataFactory,
  terminalNodeDataFactory,
} from "./helpers/node-data-factories";

import { WorkflowContext } from "src/context";
import { WorkflowProjectGenerator } from "src/project";
import { WorkflowDataNode } from "src/types/vellum";

describe("getOrderedNodes", () => {
  const getOrderedNodes = (
    workflowContext: WorkflowContext
  ): WorkflowDataNode[] => {
    const project = new WorkflowProjectGenerator({
      workflowContext,
      workflowVersionExecConfig: {
        workflowRawData: workflowContext.workflowRawData,
        inputVariables: [],
        outputVariables: [],
        stateVariables: [],
      },
      moduleName: "test",
    });

    // We access the private method here to avoid having to create a full project
    return (
      project as unknown as { getOrderedNodes(): WorkflowDataNode[] }
    ).getOrderedNodes();
  };

  const runOrderedNodesTest = (
    edgeFactoryNodePairs: EdgeFactoryNodePair[]
  ): WorkflowDataNode[] => {
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

    return getOrderedNodes(workflowContext);
  };

  it("should correctly order sequential nodes", () => {
    const nodeA = genericNodeFactory({
      id: "node-a",
      label: "Node A",
    });
    const nodeB = genericNodeFactory({
      id: "node-b",
      label: "Node B",
    });
    const nodeC = genericNodeFactory({
      id: "node-c",
      label: "Node C",
    });

    const entrypoint = entrypointNodeDataFactory();

    const orderedNodes = runOrderedNodesTest([
      [entrypoint, nodeA],
      [nodeA, nodeB],
      [nodeB, nodeC],
    ]);

    const nodeIds = orderedNodes.map((node) => node.id);
    expect(nodeIds).toEqual(["node-a", "node-b", "node-c"]);
  });

  it("should correctly order nodes with branches", () => {
    const nodeA = genericNodeFactory({
      id: "node-a",
      label: "Node A",
    });
    const nodeB = genericNodeFactory({
      id: "node-b",
      label: "Node B",
    });
    const nodeC = genericNodeFactory({
      id: "node-c",
      label: "Node C",
    });
    const nodeD = genericNodeFactory({
      id: "node-d",
      label: "Node D",
    });

    const entrypoint = entrypointNodeDataFactory();

    const orderedNodes = runOrderedNodesTest([
      [entrypoint, nodeA],
      [nodeA, nodeB],
      [nodeA, nodeC],
      [nodeB, nodeD],
      [nodeC, nodeD],
    ]);

    const nodeIds = orderedNodes.map((node) => node.id);

    // Node A must come before B and C
    expect(nodeIds.indexOf("node-a")).toBeLessThan(nodeIds.indexOf("node-b"));
    expect(nodeIds.indexOf("node-a")).toBeLessThan(nodeIds.indexOf("node-c"));

    // Both B and C must come before D
    expect(nodeIds.indexOf("node-b")).toBeLessThan(nodeIds.indexOf("node-d"));
    expect(nodeIds.indexOf("node-c")).toBeLessThan(nodeIds.indexOf("node-d"));
  });

  it("should handle parallel nodes", () => {
    const parallelNode1 = genericNodeFactory({
      id: "parallel-node-1",
      label: "Parallel Node 1",
    });
    const seqNode1 = genericNodeFactory({
      id: "seq-node-1",
      label: "Sequential Node 1",
    });
    const seqNode2 = genericNodeFactory({
      id: "seq-node-2",
      label: "Sequential Node 2",
    });
    const requestBodyNode = genericNodeFactory({
      id: "request-body-node",
      label: "Request Body Node",
    });
    const parallelNode2 = genericNodeFactory({
      id: "parallel-node-2",
      label: "Parallel Node 2",
    });

    const mergeNode = mergeNodeDataFactory().build();

    const apiNode = genericNodeFactory({
      id: "api-node",
      label: "API Node",
    });

    const finalOutput = terminalNodeDataFactory();

    const entrypoint = entrypointNodeDataFactory();

    // GIVEN the following workflow:
    // {
    //   parallelNode1
    //   >> seqNode1
    //   >> seqNode2
    //   >> requestBodyNode
    //   parallelNode2
    // }
    // >> mergeNode
    // >> apiNode
    // >> finalOutput
    const orderedNodes = runOrderedNodesTest([
      [entrypoint, parallelNode1],
      [entrypoint, parallelNode2],
      [parallelNode1, seqNode1],
      [seqNode1, seqNode2],
      [seqNode2, requestBodyNode],
      [requestBodyNode, [mergeNode, 0]],
      [parallelNode2, [mergeNode, 1]],
      [mergeNode, apiNode],
      [apiNode, finalOutput],
    ]);

    const nodeIds = orderedNodes.map((node) => node.id);

    // requestBodyNode must come before apiNode
    expect(nodeIds.indexOf("request-body-node")).toBeLessThan(
      nodeIds.indexOf("api-node")
    );

    // merge, api, finalOutput must come after requestBodyNode
    expect(nodeIds.indexOf("merge-node-1")).toBeGreaterThan(
      nodeIds.indexOf("request-body-node")
    );
    expect(nodeIds.indexOf("api-node")).toBeGreaterThan(
      nodeIds.indexOf("request-body-node")
    );
    expect(nodeIds.indexOf("terminal-node-1")).toBeGreaterThan(
      nodeIds.indexOf("request-body-node")
    );

    // merge, api, finalOutput must come after parallelNode2
    expect(nodeIds.indexOf("merge-node-1")).toBeGreaterThan(
      nodeIds.indexOf("parallel-node-2")
    );
    expect(nodeIds.indexOf("api-node")).toBeGreaterThan(
      nodeIds.indexOf("parallel-node-2")
    );
    expect(nodeIds.indexOf("terminal-node-1")).toBeGreaterThan(
      nodeIds.indexOf("parallel-node-2")
    );
  });

  it("should handle cycles", () => {
    const nodeA = genericNodeFactory({
      id: "node-a",
      label: "Node A",
    });
    const nodeB = genericNodeFactory({
      id: "node-b",
      label: "Node B",
    });
    const nodeC = genericNodeFactory({
      id: "node-c",
      label: "Node C",
    });
    const nodeD = genericNodeFactory({
      id: "node-d",
      label: "Node D",
    });

    const nodeE = genericNodeFactory({
      id: "node-e",
      label: "Node E",
    });

    const entrypoint = entrypointNodeDataFactory();

    // GIVEN a cycle A -> B -> C -> D -> B and D -> E
    const orderedNodes = runOrderedNodesTest([
      [entrypoint, nodeA],
      [nodeD, nodeE], // We put this edge here to avoid the passed-in order affecting the results
      [nodeA, nodeB],
      [nodeB, nodeC],
      [nodeC, nodeD],
      [nodeD, nodeB],
    ]);

    const nodeIds = orderedNodes.map((node) => node.id);

    // All nodes should be included in the result
    expect(nodeIds.length).toBe(5);
    expect(nodeIds.includes("node-a")).toBe(true);
    expect(nodeIds.includes("node-b")).toBe(true);
    expect(nodeIds.includes("node-c")).toBe(true);
    expect(nodeIds.includes("node-d")).toBe(true);
    expect(nodeIds.includes("node-e")).toBe(true);

    // A should come before B, C, and D
    expect(nodeIds.indexOf("node-a")).toBeLessThan(nodeIds.indexOf("node-b"));
    expect(nodeIds.indexOf("node-a")).toBeLessThan(nodeIds.indexOf("node-c"));
    expect(nodeIds.indexOf("node-a")).toBeLessThan(nodeIds.indexOf("node-d"));

    // Despite the cycle, E should come after B, C, and D
    expect(nodeIds.indexOf("node-e")).toBeGreaterThan(
      nodeIds.indexOf("node-d")
    );
    expect(nodeIds.indexOf("node-e")).toBeGreaterThan(
      nodeIds.indexOf("node-c")
    );
    expect(nodeIds.indexOf("node-e")).toBeGreaterThan(
      nodeIds.indexOf("node-b")
    );
  });
});
