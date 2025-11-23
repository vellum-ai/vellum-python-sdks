import { python } from "@fern-api/python-ast";
import { OperatorType } from "@fern-api/python-ast/OperatorType";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import {
  PORTS_CLASS_NAME,
  VELLUM_WORKFLOW_GRAPH_MODULE_PATH,
} from "src/constants";
import { Writer } from "src/generators/extensions/writer";
import {
  EntrypointNode,
  WorkflowDataNode,
  WorkflowEdge,
  WorkflowTrigger,
} from "src/types/vellum";
import { getTriggerClassInfo } from "src/utils/triggers";

import type { WorkflowContext } from "src/context";
import type { BaseNodeContext } from "src/context/node-context/base";
import type { PortContext } from "src/context/port-context";

// Fern's Python AST types are not mutable, so we need to define our own types
// so that we can mutate the graph as we traverse through the edges.
type GraphEmpty = { type: "empty" };
type GraphSet = { type: "set"; values: GraphMutableAst[] };
type GraphNodeReference = {
  type: "node_reference";
  reference: BaseNodeContext<WorkflowDataNode>;
};
type GraphPortReference = {
  type: "port_reference";
  reference: PortContext;
};
type GraphTriggerReference = {
  type: "trigger_reference";
  reference: WorkflowTrigger;
};
type GraphRightShift = {
  type: "right_shift";
  lhs: GraphMutableAst;
  rhs: GraphMutableAst;
};
type GraphMutableAst =
  | GraphEmpty
  | GraphSet
  | GraphNodeReference
  | GraphPortReference
  | GraphTriggerReference
  | GraphRightShift;

export declare namespace GraphAttribute {
  interface Args {
    workflowContext: WorkflowContext;
    unusedEdges?: Set<WorkflowEdge>;
  }
}

export class GraphAttribute extends AstNode {
  private readonly workflowContext: WorkflowContext;
  private readonly entrypointNode: EntrypointNode | null;
  private readonly astNode: python.AstNode;
  private readonly unusedEdges: Set<WorkflowEdge>;
  private readonly usedEdges = new Set<WorkflowEdge>();
  private readonly usedNodes = new Set<string>();
  private readonly mutableAst: GraphMutableAst;

  public constructor({
    workflowContext,
    unusedEdges = new Set(),
  }: GraphAttribute.Args) {
    super();
    this.workflowContext = workflowContext;
    this.unusedEdges = unusedEdges; // This will only have value after used graph is generated

    this.entrypointNode = this.workflowContext.tryGetEntrypointNode();
    this.mutableAst = this.generateGraphMutableAst();
    this.astNode = this.generateGraphAttribute();
  }

  /**
   * Generates a mutable graph AST.
   *
   * The algorithm we implement is a Breadth-First Search (BFS) that traverses through
   * the edges of the graph, starting from the entrypoint node.
   *
   * The core assumption made is that `graphMutableAst` is always a valid graph, and
   * adding a single edge to it will always produce another valid graph.
   */
  public generateGraphMutableAst(): GraphMutableAst {
    // Handle disconnected components first
    if (this.unusedEdges.size > 0) {
      const nextEdge = this.unusedEdges.values().next().value;
      if (!nextEdge) {
        // this should never happen as we check the size of the set
        return { type: "empty" };
      }
      // Group the unreachable edges into connected components
      const componentEdges = this.findConnectedComponent(
        nextEdge,
        this.unusedEdges
      );
      const rootNode = this.findRootNodes(componentEdges);

      try {
        return this.buildComponentGraph(rootNode, componentEdges);
      } catch (error) {
        console.warn(
          `Failed to build component graph for node ${rootNode}:`,
          error
        );
        return { type: "empty" };
      }
    }

    const edges = this.workflowContext.getTriggerEdges();

    // If no edges from entrypoint, return empty
    // Single disconnected nodes should be handled as unused_graphs, not main graph
    if (edges.length === 0) {
      return { type: "empty" };
    }

    // Process normal workflow with edges
    let graphMutableAst: GraphMutableAst = { type: "empty" };
    const edgesByPortId = this.workflowContext.getEdgesByPortId();
    const processedEdges = new Set<WorkflowEdge>();
    const edgesQueue = [...edges];

    while (edgesQueue.length > 0) {
      const edge = edgesQueue.shift();
      if (!edge) {
        continue;
      }

      const newMutableAst = this.addEdgeToGraph({
        edge,
        mutableAst: graphMutableAst,
        graphSourceNode: null,
      });
      processedEdges.add(edge);

      if (!newMutableAst) {
        continue;
      }

      graphMutableAst = newMutableAst;
      const targetNode = this.resolveTargetNodeId(edge.targetNodeId);
      if (!targetNode) {
        continue;
      }

      targetNode.reference.portContextsById.forEach((portContext) => {
        const edges = edgesByPortId.get(portContext.portId);
        edges?.forEach((edge) => {
          if (processedEdges.has(edge) || edgesQueue.includes(edge)) {
            return;
          }
          edgesQueue.push(edge);
        });
      });
    }

    return graphMutableAst;
  }

  public getUsedEdges(): Set<WorkflowEdge> {
    return this.usedEdges;
  }

  public getUsedNodes(): Set<string> {
    return this.usedNodes;
  }

  /**
   * Returns an array of Python AST nodes. If the GraphAttribute represents a set,
   * returns the individual elements. Otherwise, returns an array with a single element.
   */
  public getAstNodesForUnusedGraphs(): python.AstNode[] {
    if (this.mutableAst.type === "set") {
      // Convert each set member to a Python AST node
      return this.mutableAst.values.map((value) => {
        const astNode = this.getGraphAttributeAstNode(value);
        this.inheritReferences(astNode);
        return astNode;
      });
    }
    // For non-set types, return the whole thing as a single node
    return [this.astNode];
  }

  /**
   * findRootNodes is used to handle all orderings of the component
   *
   * If there is a cycle, we arbitrarily pick the first edge as the root node
   */
  private findRootNodes(componentEdges: Set<WorkflowEdge>): string {
    const incomingEdges = new Map<string, number>();

    componentEdges.forEach((edge) => {
      incomingEdges.set(
        edge.targetNodeId,
        (incomingEdges.get(edge.targetNodeId) || 0) + 1
      );
      if (!incomingEdges.has(edge.sourceNodeId)) {
        incomingEdges.set(edge.sourceNodeId, 0);
      }
    });

    // Identify nodes with zero incoming edges (roots)
    const rootNodes = new Set<string>();
    incomingEdges.forEach((count, nodeId) => {
      if (count === 0) {
        rootNodes.add(nodeId);
      }
    });

    const rootNode = rootNodes.values().next().value;
    if (!rootNode) {
      // Cycle detected, pick any node as the root
      const arbitraryEdge = componentEdges.values().next().value;
      if (arbitraryEdge) {
        return arbitraryEdge.sourceNodeId;
      }

      throw new Error("Failed to find any edge in the component");
    }

    return rootNode;
  }

  private findConnectedComponent(
    startEdge: WorkflowEdge,
    edges: Set<WorkflowEdge>
  ): Set<WorkflowEdge> {
    const component = new Set<WorkflowEdge>();
    const queue = [startEdge];

    const nodesInComponent = new Set<string>([
      startEdge.sourceNodeId,
      startEdge.targetNodeId,
    ]);

    while (queue.length > 0) {
      const edge = queue.shift();
      if (!edge || component.has(edge)) continue;

      component.add(edge);
      nodesInComponent.add(edge.sourceNodeId);
      nodesInComponent.add(edge.targetNodeId);

      for (const edge of edges) {
        if (
          !component.has(edge) &&
          (nodesInComponent.has(edge.sourceNodeId) ||
            nodesInComponent.has(edge.targetNodeId))
        ) {
          queue.push(edge);
        }
      }
    }

    return component;
  }

  private buildComponentGraph(
    rootNodeId: string,
    componentEdges: Set<WorkflowEdge>
  ): GraphMutableAst {
    try {
      const rootNode = this.workflowContext.findNodeContext(rootNodeId);
      if (!rootNode) {
        return { type: "empty" };
      }

      let graph: GraphMutableAst = {
        type: "node_reference",
        reference: rootNode,
      };

      const queue: WorkflowEdge[] = [];
      const visitedEdges = new Set<WorkflowEdge>();

      componentEdges.forEach((edge) => {
        if (edge.sourceNodeId === rootNodeId) {
          queue.push(edge);
          visitedEdges.add(edge);
        }
      });

      while (queue.length > 0) {
        const edge = queue.shift();
        if (!edge) continue;

        this.usedEdges.add(edge);
        const newGraph = this.addEdgeToGraph({
          edge,
          mutableAst: graph,
          graphSourceNode: null,
        });

        if (newGraph) {
          graph = newGraph;
        }

        // Keep processing all edges in the component even cycles
        componentEdges.forEach((e) => {
          if (!visitedEdges.has(e)) {
            visitedEdges.add(e);
            queue.push(e);
          }
        });
      }

      return graph;
    } catch (error) {
      console.warn(`Failed to process node ${rootNodeId}:`, error);
      return { type: "empty" };
    }
  }

  private resolveSourceNodeId(
    nodeId: string
  ): GraphNodeReference | GraphTriggerReference | null {
    if (this.entrypointNode?.id && nodeId === this.entrypointNode.id) {
      return null;
    }

    const trigger = this.workflowContext.triggers?.find((t) => t.id === nodeId);
    if (trigger) {
      return {
        type: "trigger_reference",
        reference: trigger,
      };
    }

    return this.resolveTargetNodeId(nodeId);
  }

  private resolveTargetNodeId(nodeId: string): GraphNodeReference | null {
    const node = this.workflowContext.findLocalNodeContext(nodeId);
    if (node) {
      return {
        type: "node_reference",
        reference: node,
      };
    }
    return null;
  }

  /**
   * Adds an edge to the graph.
   *
   * This function is the core of the algorithm. It's a recursive function that
   * traverses the graph and adds the edge to the appropriate place. The following
   * invariants must be maintained:
   * 1. The input `mutableAst` is always a valid graph.
   * 2. The output `mutableAst` must always be a valid graph.
   * 3. The edge must be added at most once.
   * 4. The method returns undefined if the edge cannot be added. This is useful for
   *    recursive calls to `addEdgeToGraph` to explore multiple paths.
   */
  private addEdgeToGraph({
    edge,
    mutableAst,
    graphSourceNode,
  }: {
    edge: WorkflowEdge;
    mutableAst: GraphMutableAst;
    graphSourceNode: GraphNodeReference | GraphTriggerReference | null;
  }): GraphMutableAst | undefined {
    this.usedEdges.add(edge);
    const sourceNodeOrTrigger = this.resolveSourceNodeId(edge.sourceNodeId);
    const targetNode = this.resolveTargetNodeId(edge.targetNodeId);
    if (!targetNode) {
      return;
    }

    if (sourceNodeOrTrigger?.type === "trigger_reference") {
      // TODO: Lots of other cases to handle here
      const sourceTrigger = sourceNodeOrTrigger;
      if (mutableAst.type === "empty") {
        return {
          type: "right_shift",
          lhs: sourceTrigger,
          rhs: targetNode,
        };
      } else {
        return {
          type: "set",
          values: [
            mutableAst,
            {
              type: "right_shift",
              lhs: sourceTrigger,
              rhs: targetNode,
            },
          ],
        };
      }
    }

    const sourceNode = sourceNodeOrTrigger;
    if (mutableAst.type === "empty") {
      return targetNode;
    } else if (mutableAst.type === "node_reference") {
      if (sourceNode && mutableAst.reference === sourceNode.reference) {
        const sourceNodePortContext = sourceNode.reference.portContextsById.get(
          edge.sourceHandleId
        );
        if (sourceNodePortContext) {
          if (sourceNodePortContext.isDefault) {
            return {
              type: "right_shift",
              lhs: mutableAst,
              rhs: targetNode,
            };
          } else {
            return {
              type: "right_shift",
              lhs: {
                type: "port_reference",
                reference: sourceNodePortContext,
              },
              rhs: targetNode,
            };
          }
        }
      } else if (sourceNode == graphSourceNode) {
        return {
          type: "set",
          values: [mutableAst, targetNode],
        };
      }
    } else if (mutableAst.type === "port_reference") {
      return this.addEdgeToPortReference({
        edge,
        mutableAst,
        sourceNode,
        targetNode,
        graphSourceNode,
      });
    } else if (mutableAst.type === "set") {
      const setAst = mutableAst as GraphSet;

      // Check if this is a cycle edge (target node already exists in the graph)
      const isCycle = this.isNodeInBranch(targetNode, setAst);
      const isSourceInGraph =
        sourceNode && this.isNodeInBranch(sourceNode, setAst);

      // Handle for direct cycles in a set
      // We already know sourceNode -> targetNode exists (it's the edge we're adding)
      // So we only need to check if targetNode -> sourceNode exists
      const sourceNodeId = sourceNode?.reference.nodeData.id;
      if (isCycle && isSourceInGraph && sourceNodeId) {
        // Self cycle edge
        if (sourceNode.reference === targetNode.reference) {
          const sourceNodePortContext =
            sourceNode.reference.portContextsById.get(edge.sourceHandleId);
          if (sourceNodePortContext && !sourceNodePortContext.isDefault) {
            return {
              type: "set",
              values: [
                ...setAst.values,
                {
                  type: "right_shift",
                  lhs: {
                    type: "port_reference",
                    reference: sourceNodePortContext,
                  },
                  rhs: targetNode,
                },
              ],
            };
          }
        }

        // Anything else
        const doesReverseEdgeExist = Array.from(
          this.workflowContext.getEdgesByPortId().values()
        )
          .flat()
          .some(
            (e) =>
              e.sourceNodeId === targetNode.reference.nodeData.id &&
              e.targetNodeId === sourceNodeId
          );
        if (doesReverseEdgeExist) {
          // Create a new set with the same values, but modify the branch that contains the source node
          const newValues = setAst.values.map((value) => {
            // Check if this branch contains the source node
            if (this.isNodeInBranch(sourceNode, value)) {
              // If it does, append the target node to create the cycle
              return {
                type: "right_shift" as const,
                lhs: value,
                rhs: targetNode,
              };
            }
            // Otherwise, leave the branch unchanged
            return value;
          });

          return {
            type: "set" as const,
            values: newValues,
          };
        }
      }

      const newSet = setAst.values.map((subAst) => {
        const canBeAdded = this.isNodeInBranch(sourceNode, subAst);
        if (!canBeAdded) {
          return { edgeAddedPriority: 0, original: subAst, value: subAst };
        }
        const newSubAst = this.addEdgeToGraph({
          edge,
          mutableAst: subAst,
          graphSourceNode,
        });
        if (!newSubAst) {
          return { edgeAddedPriority: 0, original: subAst, value: subAst };
        }

        if (subAst.type !== "set" && newSubAst.type === "set") {
          return {
            edgeAddedPriority: 1,
            original: subAst,
            value: newSubAst,
          };
        }

        if (
          subAst.type === "set" &&
          newSubAst.type === "set" &&
          newSubAst.values.length > subAst.values.length
        ) {
          return {
            edgeAddedPriority: 1,
            original: subAst,
            value: newSubAst,
          };
        }

        return { edgeAddedPriority: 2, original: subAst, value: newSubAst };
      });
      if (newSet.every(({ edgeAddedPriority }) => edgeAddedPriority === 0)) {
        if (sourceNode == graphSourceNode) {
          return {
            type: "set",
            values: [...setAst.values, targetNode],
          };
        } else {
          return;
        }
      }

      // We only want to add the edge to _one_ of the set members.
      // So we need to pick the one with the highest priority,
      // tie breaking by earliest index.
      const { index: maxPriorityIndex } = newSet.reduce(
        (prev, curr, index) => {
          if (curr.edgeAddedPriority > prev.priority) {
            return { index, priority: curr.edgeAddedPriority };
          }
          return prev;
        },
        {
          index: -1,
          priority: -1,
        }
      );

      const newSetAst: GraphSet = {
        type: "set",
        values: newSet.map(({ value, original }, index) =>
          index == maxPriorityIndex ? value : original
        ),
      };

      const flattenedNewSetAst = this.flattenSet(newSetAst);

      return this.optimizeSetThroughCommonTarget(
        flattenedNewSetAst,
        targetNode
      );
    } else if (mutableAst.type === "right_shift") {
      return this.addEdgeToRightShift({
        edge,
        mutableAst,
        graphSourceNode,
      });
    }

    return;
  }

  /**
   * Adds an edge to a Graph that is just a Port Reference. Three main cases:
   * 1. The edge's source node is the same port as the existing AST.
   *    Transforms `A.Ports.a` to `A.Ports.a >> B`
   * 2. The edge's source node is the same node as the existing AST, but a different port.
   *    Transforms `A.Ports.a` to `{ A.Ports.a, A.Ports.b >> B }`
   * 3. The edge's source node is the graph's source node feeding into the AST.
   *    Transforms `A.Ports.a` to `{ A.Ports.a, B }`
   */
  private addEdgeToPortReference({
    edge,
    mutableAst,
    sourceNode,
    targetNode,
    graphSourceNode,
  }: {
    edge: WorkflowEdge;
    mutableAst: GraphPortReference;
    sourceNode: GraphNodeReference | null;
    targetNode: GraphNodeReference;
    graphSourceNode: GraphNodeReference | GraphTriggerReference | null;
  }): GraphMutableAst | undefined {
    if (sourceNode) {
      const sourceNodePortContext = sourceNode.reference.portContextsById.get(
        edge.sourceHandleId
      );
      if (sourceNodePortContext === mutableAst.reference) {
        return {
          type: "right_shift",
          lhs: mutableAst,
          rhs: targetNode,
        };
      }
      if (
        sourceNodePortContext?.nodeContext === mutableAst.reference.nodeContext
      ) {
        return {
          type: "set",
          values: [
            mutableAst,
            {
              type: "right_shift",
              lhs: {
                type: "port_reference",
                reference: sourceNodePortContext,
              },
              rhs: targetNode,
            },
          ],
        };
      }
    } else if (sourceNode == graphSourceNode) {
      return {
        type: "set",
        values: [mutableAst, targetNode],
      };
    }
    return;
  }

  /**
   * Adds an edge to a Graph that is just a Right Shift between two graphs. We prioritize
   * adding the edge to the left hand side of the right shift before then checking the right hand side.
   * When checking the right hand side, we calculate a new graphSourceNode which is the terminals of the
   * left hand side.
   */
  private addEdgeToRightShift({
    edge,
    mutableAst,
    graphSourceNode,
  }: {
    edge: WorkflowEdge;
    mutableAst: GraphRightShift;
    graphSourceNode: GraphNodeReference | GraphTriggerReference | null;
  }): GraphMutableAst | undefined {
    const newLhs = this.addEdgeToGraph({
      edge,
      mutableAst: mutableAst.lhs,
      graphSourceNode,
    });

    if (newLhs) {
      const newSetAst: GraphSet = {
        type: "set",
        values: [mutableAst, newLhs],
      };
      if (this.isPlural(newSetAst)) {
        const newAstSources = newSetAst.values.flatMap((value) =>
          this.getAstSources(value)
        );

        const uniqueAstSourceIds = new Set(
          newAstSources.map((source) => source.reference.portId)
        );
        if (uniqueAstSourceIds.size === 1 && newAstSources[0]) {
          const portReference = newAstSources[0];
          return {
            type: "right_shift",
            lhs: portReference.reference.isDefault
              ? {
                  type: "node_reference",
                  reference: portReference.reference.nodeContext,
                }
              : portReference,
            rhs: this.popSources(newSetAst),
          };
        }
      }

      const flattenedNewSetAst = this.flattenSet(newSetAst);
      if (mutableAst.rhs.type === "node_reference") {
        return this.optimizeSetThroughCommonTarget(
          flattenedNewSetAst,
          mutableAst.rhs
        );
      }
      return flattenedNewSetAst;
    }

    const lhsTerminals = this.getAstTerminals(mutableAst.lhs);
    const lhsTerminal = lhsTerminals[0];
    if (!lhsTerminal) {
      return;
    }

    const newRhs = this.addEdgeToGraph({
      edge,
      mutableAst: mutableAst.rhs,
      graphSourceNode: lhsTerminal,
    });
    if (newRhs) {
      return {
        type: "right_shift",
        lhs: mutableAst.lhs,
        rhs: newRhs,
      };
    }

    return;
  }

  /**
   * Checks if the AST contains an edge. We consider a `set` to be plural if all of its members are plural.
   */
  private isPlural(mutableAst: GraphMutableAst): boolean {
    return (
      mutableAst.type === "right_shift" ||
      (mutableAst.type === "set" &&
        mutableAst.values.every((v) => this.isPlural(v)))
    );
  }

  /**
   * Gets the sources of the AST. The AST source are the set of Port References that
   * serve as the entrypoints to the Graph. In the case of a set, it's the set of sources
   * of each of the set's members.
   */
  private getAstSources = (
    mutableAst: GraphMutableAst
  ): GraphPortReference[] => {
    if (mutableAst.type === "empty") {
      return [];
    } else if (mutableAst.type === "node_reference") {
      const defaultPort = mutableAst.reference.defaultPortContext;
      if (defaultPort) {
        return [
          {
            type: "port_reference",
            reference: defaultPort,
          },
        ];
      }
      return [];
    } else if (mutableAst.type === "set") {
      return mutableAst.values.flatMap((val) => this.getAstSources(val));
    } else if (mutableAst.type === "right_shift") {
      return this.getAstSources(mutableAst.lhs);
    } else if (mutableAst.type == "port_reference") {
      return [mutableAst];
    } else {
      return [];
    }
  };

  /**
   * Gets the terminals of the AST. The AST terminals are the set of Node References that
   * serve as the exit points of the Graph. In the case of a set, it's the set of
   * terminals of each of the set's members.
   */
  private getAstTerminals(
    mutableAst: GraphMutableAst
  ): (GraphNodeReference | GraphTriggerReference)[] {
    if (mutableAst.type === "empty") {
      return [];
    } else if (
      mutableAst.type === "node_reference" ||
      mutableAst.type === "trigger_reference"
    ) {
      return [mutableAst];
    } else if (mutableAst.type === "set") {
      return mutableAst.values.flatMap((val) => this.getAstTerminals(val));
    } else if (mutableAst.type === "right_shift") {
      return this.getAstTerminals(mutableAst.rhs);
    } else if (mutableAst.type == "port_reference") {
      return [
        {
          type: "node_reference",
          reference: mutableAst.reference.nodeContext,
        },
      ];
    } else {
      return [];
    }
  }

  /**
   * Optimizes the set by seeing if there's a common node across all branches
   * that could be used as a target node for the set. The base case example is:
   *
   * ```
   * {
   *   A >> C,
   *   B >> C,
   * }
   * ```
   *
   * This could be optimized to:
   *
   * ```
   * { A, B } >> C
   * ```
   */
  private optimizeSetThroughCommonTarget(
    mutableSetAst: GraphSet,
    targetNode: GraphNodeReference
  ): GraphMutableAst | undefined {
    if (
      this.canBranchBeSplitByTargetNode({
        targetNode,
        mutableAst: mutableSetAst,
        isRoot: true,
      })
    ) {
      const newLhs: GraphSet = {
        type: "set",
        values: [],
      };
      let longestRhs: GraphMutableAst = { type: "empty" };
      for (const branch of mutableSetAst.values) {
        const { lhs, rhs } = this.splitBranchByTargetNode(targetNode, branch);
        if (this.getBranchSize(rhs) > this.getBranchSize(longestRhs)) {
          longestRhs = rhs;
        }
        newLhs.values.push(lhs);
      }

      // In a situation where the graph was:
      // {
      //   A >> B >> C,
      //   C >> D,
      // }
      //
      // The longest rhs would be C >> D, but it would create an empty set member.
      // In this case, we want just `D` to be the longest rhs.
      if (newLhs.values.some((v) => v.type === "empty")) {
        const sources = this.getAstSources(longestRhs);
        const readjustedSource = sources[0];
        if (readjustedSource) {
          const newLongestRhs = this.popSources(longestRhs);
          return {
            type: "right_shift",
            lhs: this.appendNodeToAst(readjustedSource, newLhs),
            rhs: newLongestRhs,
          };
        }
      }

      return {
        type: "right_shift",
        lhs: this.flattenSet(newLhs),
        rhs: longestRhs,
      };
    }

    return mutableSetAst;
  }

  /**
   * Flattens a set of GraphMutableAsts into a single set of GraphMutableAsts. Any entries
   * that are subsets of previous members are removed.
   */
  private flattenSet(setAst: GraphSet): GraphSet {
    const newEntries: GraphMutableAst[] = [];
    for (const entry of setAst.values) {
      const potentialEntries =
        entry.type === "set" ? this.flattenSet(entry).values : [entry];
      for (const potentialEntry of potentialEntries) {
        if (
          newEntries.some((e) =>
            this.isGraphSubsetOfTargetGraph(potentialEntry, e)
          )
        ) {
          continue;
        }
        newEntries.push(potentialEntry);
      }
    }
    return {
      type: "set",
      values: newEntries,
    };
  }

  /**
   * Checks if the source graph is a subset of the target graph.
   */
  private isGraphSubsetOfTargetGraph(
    sourceGraph: GraphMutableAst,
    targetGraph: GraphMutableAst
  ): boolean {
    if (sourceGraph.type === "empty") {
      return true;
    }

    if (sourceGraph.type === "node_reference") {
      return this.getAstSources(targetGraph).some(
        (s) => s.reference.nodeContext === sourceGraph.reference
      );
    }

    if (sourceGraph.type === "port_reference") {
      return this.getAstSources(targetGraph).some(
        (s) => s.reference === sourceGraph.reference
      );
    }

    // TODO: We likely need to handle all the cases here, but deferring until
    // the test cases to force the issue arise.
    return false;
  }

  /**
   * Checks if targetNode is in the branch
   */
  private isNodeInBranch(
    targetNode: GraphNodeReference | null,
    mutableAst: GraphMutableAst
  ): boolean {
    if (targetNode == null) {
      return false;
    }
    if (
      mutableAst.type === "node_reference" &&
      mutableAst.reference === targetNode.reference
    ) {
      return true;
    } else if (mutableAst.type === "set") {
      return mutableAst.values.some((value) =>
        this.isNodeInBranch(targetNode, value)
      );
    } else if (mutableAst.type === "right_shift") {
      return (
        this.isNodeInBranch(targetNode, mutableAst.lhs) ||
        this.isNodeInBranch(targetNode, mutableAst.rhs)
      );
    } else if (mutableAst.type === "port_reference") {
      return mutableAst.reference.nodeContext === targetNode.reference;
    }
    return false;
  }

  /**
   * Checks to see if the branch can be split by the target node. This is similar
   * to `isNodeInBranch`, but for sets requires that the target node is splittable
   * across all members
   */
  private canBranchBeSplitByTargetNode({
    targetNode,
    mutableAst,
    isRoot,
  }: {
    targetNode: GraphNodeReference | null;
    mutableAst: GraphMutableAst;
    isRoot: boolean;
  }): boolean {
    if (targetNode == null) {
      return false;
    }
    if (mutableAst.type === "set") {
      return mutableAst.values.every((value) =>
        this.canBranchBeSplitByTargetNode({
          targetNode,
          mutableAst: value,
          isRoot: true,
        })
      );
    }
    if (
      mutableAst.type === "node_reference" &&
      mutableAst.reference === targetNode.reference
    ) {
      return !isRoot;
    }
    if (mutableAst.type === "right_shift") {
      return (
        this.canBranchBeSplitByTargetNode({
          targetNode,
          mutableAst: mutableAst.lhs,
          isRoot: false,
        }) ||
        this.canBranchBeSplitByTargetNode({
          targetNode,
          mutableAst: mutableAst.rhs,
          isRoot: false,
        })
      );
    }
    if (mutableAst.type === "port_reference") {
      return false;
    }
    return false;
  }

  /**
   * Gets the size of the branch
   */
  private getBranchSize(mutableAst: GraphMutableAst): number {
    if (mutableAst.type === "empty") {
      return 0;
    } else if (
      mutableAst.type === "node_reference" ||
      mutableAst.type === "port_reference"
    ) {
      return 1;
    } else if (mutableAst.type === "set") {
      return Math.max(
        ...mutableAst.values.map((value) => this.getBranchSize(value))
      );
    } else if (mutableAst.type === "right_shift") {
      return (
        this.getBranchSize(mutableAst.lhs) + this.getBranchSize(mutableAst.rhs)
      );
    }
    return 0;
  }

  /**
   * Gets the nodes in the branch
   */
  private getNodesInBranch(
    mutableAst: GraphMutableAst
  ): BaseNodeContext<WorkflowDataNode>[] {
    if (mutableAst.type === "node_reference") {
      return [mutableAst.reference];
    } else if (mutableAst.type === "set") {
      return mutableAst.values.flatMap((value) => this.getNodesInBranch(value));
    } else if (mutableAst.type === "right_shift") {
      return [
        ...this.getNodesInBranch(mutableAst.lhs),
        ...this.getNodesInBranch(mutableAst.rhs),
      ];
    } else if (mutableAst.type === "port_reference") {
      return [mutableAst.reference.nodeContext];
    } else {
      return [];
    }
  }

  /**
   * Splits the branch by the target node into two ASTs.
   */
  private splitBranchByTargetNode(
    targetNode: GraphNodeReference,
    mutableAst: GraphMutableAst
  ): { lhs: GraphMutableAst; rhs: GraphMutableAst } {
    if (mutableAst.type === "empty") {
      return { lhs: { type: "empty" }, rhs: { type: "empty" } };
    } else if (
      mutableAst.type === "node_reference" &&
      mutableAst.reference === targetNode.reference
    ) {
      return { lhs: { type: "empty" }, rhs: mutableAst };
    } else if (
      mutableAst.type === "node_reference" &&
      mutableAst.reference != targetNode.reference
    ) {
      return { lhs: mutableAst, rhs: { type: "empty" } };
    } else if (
      mutableAst.type === "port_reference" &&
      mutableAst.reference.nodeContext === targetNode.reference
    ) {
      return { lhs: { type: "empty" }, rhs: mutableAst };
    } else if (
      mutableAst.type === "port_reference" &&
      mutableAst.reference.nodeContext != targetNode.reference
    ) {
      return { lhs: mutableAst, rhs: { type: "empty" } };
    } else if (mutableAst.type === "set") {
      if (this.startsWithTargetNode(targetNode, mutableAst)) {
        return { lhs: { type: "empty" }, rhs: mutableAst };
      }
      return { lhs: mutableAst, rhs: { type: "empty" } };
    } else if (mutableAst.type === "right_shift") {
      if (this.isNodeInBranch(targetNode, mutableAst.lhs)) {
        const splitLhs = this.splitBranchByTargetNode(
          targetNode,
          mutableAst.lhs
        );
        return {
          lhs: splitLhs.lhs,
          rhs: this.optimizeRightShift({
            type: "right_shift",
            lhs: splitLhs.rhs,
            rhs: mutableAst.rhs,
          }),
        };
      } else if (this.isNodeInBranch(targetNode, mutableAst.rhs)) {
        const splitRhs = this.splitBranchByTargetNode(
          targetNode,
          mutableAst.rhs
        );
        return {
          lhs: this.optimizeRightShift({
            type: "right_shift",
            lhs: mutableAst.lhs,
            rhs: splitRhs.lhs,
          }),
          rhs: splitRhs.rhs,
        };
      }
    }

    return { lhs: { type: "empty" }, rhs: { type: "empty" } };
  }

  /**
   * Optimizes a right shift node by pruning the empty from either side.
   */
  private optimizeRightShift(mutableAst: GraphRightShift): GraphMutableAst {
    if (mutableAst.lhs.type === "empty" && mutableAst.rhs.type !== "empty") {
      return mutableAst.rhs;
    } else if (
      mutableAst.rhs.type === "empty" &&
      mutableAst.lhs.type !== "empty"
    ) {
      return mutableAst.lhs;
    } else if (
      mutableAst.lhs.type === "empty" &&
      mutableAst.rhs.type === "empty"
    ) {
      return { type: "empty" };
    }
    return mutableAst;
  }

  /**
   * Pops the source node from the AST, returning a new AST without the source node.
   *
   * Example:
   *
   * ```
   * A >> B >> C
   * ```
   *
   * Becomes:
   *
   * ```
   * B >> C
   * ```
   */
  private popSources = (mutableAst: GraphMutableAst): GraphMutableAst => {
    if (mutableAst.type === "set") {
      return this.flattenSet({
        type: "set",
        values: mutableAst.values.map(this.popSources),
      });
    } else if (mutableAst.type === "right_shift") {
      const newLhs = this.popSources(mutableAst.lhs);
      if (newLhs.type === "empty") {
        return mutableAst.rhs;
      }
      return {
        type: "right_shift",
        lhs: newLhs,
        rhs: mutableAst.rhs,
      };
    } else {
      return { type: "empty" };
    }
  };

  /**
   * Appends a node to the AST.
   */
  private appendNodeToAst(
    node: GraphPortReference,
    ast: GraphMutableAst
  ): GraphMutableAst {
    if (ast.type === "empty") {
      return node.reference.isDefault
        ? { type: "node_reference", reference: node.reference.nodeContext }
        : node;
    }
    if (
      ast.type === "node_reference" ||
      ast.type === "port_reference" ||
      ast.type === "trigger_reference"
    ) {
      return {
        type: "right_shift",
        lhs: ast,
        rhs: node.reference.isDefault
          ? { type: "node_reference", reference: node.reference.nodeContext }
          : node,
      };
    }
    if (ast.type === "set") {
      return {
        type: "set",
        values: ast.values.map((value) => this.appendNodeToAst(node, value)),
      };
    }
    if (ast.type === "right_shift") {
      return {
        type: "right_shift",
        lhs: ast.lhs,
        rhs: this.appendNodeToAst(node, ast.rhs),
      };
    }
    return ast;
  }

  private startsWithTargetNode = (
    targetNode: GraphNodeReference,
    mutableAst: GraphMutableAst
  ): boolean => {
    if (mutableAst.type === "node_reference") {
      return mutableAst.reference === targetNode.reference;
    } else if (mutableAst.type === "port_reference") {
      return mutableAst.reference.nodeContext === targetNode.reference;
    } else if (mutableAst.type === "set") {
      return mutableAst.values.every((value) =>
        this.startsWithTargetNode(targetNode, value)
      );
    } else if (mutableAst.type === "right_shift") {
      return this.startsWithTargetNode(targetNode, mutableAst.lhs);
    }
    return false;
  };

  /**
   * Translates our mutable graph AST into a Fern-native Python AST node.
   */
  private getGraphAttributeAstNode(
    mutableAst: GraphMutableAst,
    useWrap: boolean = false
  ): AstNode {
    if (mutableAst.type === "empty") {
      return python.accessAttribute({
        lhs: python.reference({
          name: "Graph",
          modulePath: VELLUM_WORKFLOW_GRAPH_MODULE_PATH,
        }),
        rhs: python.invokeMethod({
          methodReference: python.reference({
            name: "empty",
          }),
          arguments_: [],
        }),
      });
    }

    if (mutableAst.type === "node_reference") {
      return python.reference({
        name: mutableAst.reference.nodeClassName,
        modulePath: mutableAst.reference.nodeModulePath,
      });
    }

    if (mutableAst.type === "trigger_reference") {
      const { className, modulePath } = getTriggerClassInfo(
        mutableAst.reference,
        this.workflowContext
      );
      return python.reference({
        name: className,
        modulePath: modulePath,
      });
    }

    if (mutableAst.type === "port_reference") {
      return python.reference({
        name: mutableAst.reference.nodeContext.nodeClassName,
        modulePath: mutableAst.reference.nodeContext.nodeModulePath,
        attribute: mutableAst.reference.isDefault
          ? undefined
          : [PORTS_CLASS_NAME, mutableAst.reference.portName],
      });
    }

    if (mutableAst.type === "set") {
      const setAst = python.TypeInstantiation.set(
        mutableAst.values.map((ast) => this.getGraphAttributeAstNode(ast)),
        {
          endWithComma: true,
        }
      );
      if (useWrap) {
        return python.accessAttribute({
          lhs: python.reference({
            name: "Graph",
            modulePath: VELLUM_WORKFLOW_GRAPH_MODULE_PATH,
          }),
          rhs: python.invokeMethod({
            methodReference: python.reference({
              name: "from_set",
            }),
            arguments_: [python.methodArgument({ value: setAst })],
          }),
        });
      }
      return setAst;
    }

    if (mutableAst.type === "right_shift") {
      const lhs = this.getGraphAttributeAstNode(mutableAst.lhs, useWrap);
      const rhs = this.getGraphAttributeAstNode(
        mutableAst.rhs,
        mutableAst.lhs.type === "set"
      );
      if (!lhs || !rhs) {
        return python.TypeInstantiation.none();
      }
      return python.operator({
        operator: OperatorType.RightShift,
        lhs,
        rhs,
      });
    }

    return python.TypeInstantiation.none();
  }

  private generateGraphAttribute(): AstNode {
    const astNode = this.getGraphAttributeAstNode(this.mutableAst);
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }

  private debug(mutableAst: GraphMutableAst | undefined): string {
    if (!mutableAst) {
      return "NULL";
    }

    if (mutableAst.type === "right_shift") {
      return `${this.debug(mutableAst.lhs)} >> ${this.debug(mutableAst.rhs)}`;
    }

    if (mutableAst.type === "node_reference") {
      return mutableAst.reference.nodeClassName;
    }

    if (mutableAst.type === "trigger_reference") {
      const { className } = getTriggerClassInfo(
        mutableAst.reference,
        this.workflowContext
      );
      return className;
    }

    if (mutableAst.type === "port_reference") {
      return `${mutableAst.reference.nodeContext.nodeClassName}.Ports.${mutableAst.reference.portName}`;
    }

    if (mutableAst.type === "set") {
      return `{${mutableAst.values
        .map((value) => this.debug(value))
        .join(", ")}}`;
    }

    if (mutableAst.type === "empty") {
      return "NULL";
    }

    return "";
  }
}
