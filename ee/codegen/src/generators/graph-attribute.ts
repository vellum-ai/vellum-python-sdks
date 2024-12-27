import { python } from "@fern-api/python-ast";
import { OperatorType } from "@fern-api/python-ast/OperatorType";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { PORTS_CLASS_NAME } from "src/constants";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { WorkflowDataNode, WorkflowEdge } from "src/types/vellum";

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
  | GraphRightShift;

export declare namespace GraphAttribute {
  interface Args {
    entrypointNodeEdges: WorkflowEdge[];
    entrypointNodeId: string;
    edgesByPortId: Map<string, WorkflowEdge[]>;
    workflowContext: WorkflowContext;
  }
}

export class GraphAttribute extends AstNode {
  private readonly workflowContext: WorkflowContext;
  private readonly edgesByPortId: Map<string, WorkflowEdge[]>;
  private readonly entrypointNodeEdges: WorkflowEdge[];
  private readonly entrypointNodeId: string;
  private readonly astNode: python.AstNode;

  public constructor({
    entrypointNodeEdges,
    entrypointNodeId,
    edgesByPortId,
    workflowContext,
  }: GraphAttribute.Args) {
    super();
    this.entrypointNodeEdges = entrypointNodeEdges;
    this.entrypointNodeId = entrypointNodeId;
    this.workflowContext = workflowContext;
    this.edgesByPortId = edgesByPortId;

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
  private generateGraphMutableAst(): GraphMutableAst {
    let graphMutableAst: GraphMutableAst = { type: "empty" };
    const edgesQueue = [...this.entrypointNodeEdges];
    const processedEdges = new Set<WorkflowEdge>();

    while (edgesQueue.length > 0) {
      const edge = edgesQueue.shift();
      if (!edge) {
        continue;
      }

      const sourceNode =
        edge.sourceNodeId === this.entrypointNodeId
          ? null
          : this.workflowContext.getNodeContext(edge.sourceNodeId);

      const targetNode = this.workflowContext.getNodeContext(edge.targetNodeId);
      if (!targetNode) {
        processedEdges.add(edge);
        continue;
      }

      const isPlural = (mutableAst: GraphMutableAst): boolean => {
        return (
          mutableAst.type === "right_shift" ||
          (mutableAst.type === "set" && mutableAst.values.every(isPlural))
        );
      };

      const getAstSources = (
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
          return mutableAst.values.flatMap(getAstSources);
        } else if (mutableAst.type === "right_shift") {
          return getAstSources(mutableAst.lhs);
        } else if (mutableAst.type == "port_reference") {
          return [mutableAst];
        } else {
          return [];
        }
      };

      const getAstTerminals = (
        mutableAst: GraphMutableAst
      ): GraphNodeReference[] => {
        if (mutableAst.type === "empty") {
          return [];
        } else if (mutableAst.type === "node_reference") {
          return [mutableAst];
        } else if (mutableAst.type === "set") {
          return mutableAst.values.flatMap(getAstTerminals);
        } else if (mutableAst.type === "right_shift") {
          return getAstTerminals(mutableAst.rhs);
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
      };

      const popSources = (mutableAst: GraphMutableAst): GraphMutableAst => {
        if (mutableAst.type === "set") {
          return {
            type: "set",
            values: mutableAst.values.map(popSources),
          };
        } else if (mutableAst.type === "right_shift") {
          const newLhs = popSources(mutableAst.lhs);
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

      const addEdgeToGraph = (
        mutableAst: GraphMutableAst,
        graphSourceNode: BaseNodeContext<WorkflowDataNode> | null
      ): GraphMutableAst | undefined => {
        if (mutableAst.type === "empty") {
          return {
            type: "node_reference",
            reference: targetNode,
          };
        } else if (mutableAst.type === "node_reference") {
          if (sourceNode && mutableAst.reference === sourceNode) {
            const sourceNodePortContext = sourceNode.portContextsById.get(
              edge.sourceHandleId
            );
            if (sourceNodePortContext) {
              if (sourceNodePortContext.isDefault) {
                return {
                  type: "right_shift",
                  lhs: mutableAst,
                  rhs: { type: "node_reference", reference: targetNode },
                };
              } else {
                return {
                  type: "right_shift",
                  lhs: {
                    type: "port_reference",
                    reference: sourceNodePortContext,
                  },
                  rhs: { type: "node_reference", reference: targetNode },
                };
              }
            }
          } else if (sourceNode == graphSourceNode) {
            return {
              type: "set",
              values: [
                mutableAst,
                { type: "node_reference", reference: targetNode },
              ],
            };
          }
        } else if (mutableAst.type === "port_reference") {
          if (sourceNode) {
            const sourceNodePortContext = sourceNode.portContextsById.get(
              edge.sourceHandleId
            );
            if (sourceNodePortContext === mutableAst.reference) {
              return {
                type: "right_shift",
                lhs: mutableAst,
                rhs: { type: "node_reference", reference: targetNode },
              };
            }
          } else if (sourceNode == graphSourceNode) {
            return {
              type: "set",
              values: [
                mutableAst,
                { type: "node_reference", reference: targetNode },
              ],
            };
          }
        } else if (mutableAst.type === "set") {
          const newSet = mutableAst.values.map((subAst) => {
            const canBeAdded = this.isNodeInBranch(sourceNode, subAst);
            if (!canBeAdded) {
              return { edgeAddedPriority: 0, original: subAst, value: subAst };
            }

            const newSubAst = addEdgeToGraph(subAst, graphSourceNode);
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
          if (
            newSet.every(({ edgeAddedPriority }) => edgeAddedPriority === 0)
          ) {
            if (sourceNode == graphSourceNode) {
              return {
                type: "set",
                values: [
                  ...mutableAst.values,
                  { type: "node_reference", reference: targetNode },
                ],
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
          const newLhs = addEdgeToGraph(mutableAst.lhs, graphSourceNode);

          if (newLhs) {
            const newSetAst: GraphSet = {
              type: "set",
              values: [mutableAst, newLhs],
            };
            if (isPlural(newSetAst)) {
              const newAstSources = newSetAst.values.flatMap((value) =>
                getAstSources(value)
              );

              const uniqueAstSourceIds = new Set(
                newAstSources.map((source) => source.reference.portId)
              );
              if (uniqueAstSourceIds.size === 1 && newAstSources[0]) {
                // If all the sources are the same, we can simplify the graph into a
                // right shift between the source node and the set.
                const portReference = newAstSources[0];
                return {
                  type: "right_shift",
                  lhs: portReference.reference.isDefault
                    ? {
                        type: "node_reference",
                        reference: portReference.reference.nodeContext,
                      }
                    : portReference,
                  rhs: popSources(newSetAst),
                };
              }
            }
            return newSetAst;
          }

          if (
            mutableAst.lhs.type == "port_reference" &&
            sourceNode &&
            mutableAst.lhs.reference.nodeContext == sourceNode
          ) {
            const sourcePortContext = sourceNode.portContextsById.get(
              edge.sourceHandleId
            );
            if (sourcePortContext) {
              return {
                type: "set",
                values: [
                  mutableAst,
                  {
                    type: "right_shift",
                    lhs: {
                      type: "port_reference",
                      reference: sourcePortContext,
                    },
                    rhs: { type: "node_reference", reference: targetNode },
                  },
                ],
              };
            }
            return;
          }

          const lhsTerminals = getAstTerminals(mutableAst.lhs);
          const lhsTerminal = lhsTerminals[0];
          if (!lhsTerminal) {
            return;
          }

          const newRhs = addEdgeToGraph(mutableAst.rhs, lhsTerminal.reference);
          if (newRhs) {
            if (lhsTerminals.length > 1 && newRhs.type === "set") {
              throw new Error(
                "Adding an edge between two sets is not supported"
              );
            }
            return {
              type: "right_shift",
              lhs: mutableAst.lhs,
              rhs: newRhs,
            };
          }
        }

        return;
      };

      const newMutableAst = addEdgeToGraph(graphMutableAst, null);
      processedEdges.add(edge);

      if (!newMutableAst) {
        continue;
      }

      graphMutableAst = newMutableAst;
      targetNode.portContextsById.forEach((portContext) => {
        const edges = this.edgesByPortId.get(portContext.portId);
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
    newSetAst: GraphSet,
    targetNode: BaseNodeContext<WorkflowDataNode>
  ): GraphMutableAst | undefined {
    if (this.canBranchBeSplitByTargetNode(targetNode, newSetAst)) {
      const newLhs: GraphSet = {
        type: "set",
        values: [],
      };
      let longestRhs: GraphMutableAst = { type: "empty" };
      for (const branch of newSetAst.values) {
        const { lhs, rhs } = this.splitBranchByTargetNode(targetNode, branch);
        if (this.getBranchSize(rhs) > this.getBranchSize(longestRhs)) {
          longestRhs = rhs;
        }
        newLhs.values.push(lhs);
      }
      return {
        type: "right_shift",
        lhs: newLhs,
        rhs: longestRhs,
      };
    }

    return newSetAst;
  }

  private flattenSet(setAst: GraphSet): GraphSet {
    return {
      type: "set",
      values: setAst.values.flatMap((value) => {
        if (value.type === "set") {
          return this.flattenSet(value).values;
        }
        return [value];
      }),
    };
  }

  /**
   * Checks if targetNode is in the branch
   */
  private isNodeInBranch(
    targetNode: BaseNodeContext<WorkflowDataNode> | null,
    mutableAst: GraphMutableAst
  ): boolean {
    if (targetNode == null) {
      return false;
    }
    if (
      mutableAst.type === "node_reference" &&
      mutableAst.reference === targetNode
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
      return mutableAst.reference.nodeContext === targetNode;
    }
    return false;
  }

  /**
   * Checks to see if the branch can be split by the target node. This is similar
   * to `isNodeInBranch`, but for sets requires that the target node is splittable
   * across all members
   */
  private canBranchBeSplitByTargetNode(
    targetNode: BaseNodeContext<WorkflowDataNode> | null,
    mutableAst: GraphMutableAst
  ): boolean {
    if (targetNode == null) {
      return false;
    }
    if (mutableAst.type === "set") {
      return mutableAst.values.every((value) =>
        this.canBranchBeSplitByTargetNode(targetNode, value)
      );
    }
    if (
      mutableAst.type === "node_reference" &&
      mutableAst.reference === targetNode
    ) {
      return true;
    }
    if (mutableAst.type === "right_shift") {
      return (
        this.canBranchBeSplitByTargetNode(targetNode, mutableAst.lhs) ||
        this.canBranchBeSplitByTargetNode(targetNode, mutableAst.rhs)
      );
    }
    if (mutableAst.type === "port_reference") {
      return mutableAst.reference.nodeContext === targetNode;
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
      mutableAst.type === "port_reference" ||
      mutableAst.type === "set"
    ) {
      return 1;
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
    targetNode: BaseNodeContext<WorkflowDataNode>,
    mutableAst: GraphMutableAst
  ): { lhs: GraphMutableAst; rhs: GraphMutableAst } {
    if (mutableAst.type === "empty") {
      return { lhs: { type: "empty" }, rhs: { type: "empty" } };
    } else if (
      mutableAst.type === "node_reference" &&
      mutableAst.reference === targetNode
    ) {
      return { lhs: { type: "empty" }, rhs: mutableAst };
    } else if (
      mutableAst.type === "node_reference" &&
      mutableAst.reference != targetNode
    ) {
      return { lhs: mutableAst, rhs: { type: "empty" } };
    } else if (
      mutableAst.type === "port_reference" &&
      mutableAst.reference.nodeContext === targetNode
    ) {
      return { lhs: { type: "empty" }, rhs: mutableAst };
    } else if (
      mutableAst.type === "port_reference" &&
      mutableAst.reference.nodeContext != targetNode
    ) {
      return { lhs: mutableAst, rhs: { type: "empty" } };
    } else if (mutableAst.type === "set") {
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
   * Translates our mutable graph AST into a Fern-native Python AST node.
   */
  private getGraphAttributeAstNode(mutableAst: GraphMutableAst): AstNode {
    if (mutableAst.type === "empty") {
      return python.TypeInstantiation.none();
    }

    if (mutableAst.type === "node_reference") {
      return python.reference({
        name: mutableAst.reference.nodeClassName,
        modulePath: mutableAst.reference.nodeModulePath,
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
      return python.TypeInstantiation.set(
        mutableAst.values.map((ast) => this.getGraphAttributeAstNode(ast)),
        {
          endWithComma: true,
        }
      );
    }

    if (mutableAst.type === "right_shift") {
      const lhs = this.getGraphAttributeAstNode(mutableAst.lhs);
      const rhs = this.getGraphAttributeAstNode(mutableAst.rhs);
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
    const graphMutableAst = this.generateGraphMutableAst();
    const astNode = this.getGraphAttributeAstNode(graphMutableAst);
    this.inheritReferences(astNode);
    return astNode;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }

  private debug(mutableAst: GraphMutableAst): string {
    if (mutableAst.type === "right_shift") {
      return `${this.debug(mutableAst.lhs)} >> ${this.debug(mutableAst.rhs)}`;
    }

    if (mutableAst.type === "node_reference") {
      return mutableAst.reference.nodeClassName;
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
