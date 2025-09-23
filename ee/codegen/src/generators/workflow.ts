import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { Reference } from "@fern-api/python-ast/Reference";
import { Type } from "@fern-api/python-ast/Type";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_WORKFLOW_MODULE_NAME,
  OUTPUTS_CLASS_NAME,
  PORTS_CLASS_NAME,
  VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
  VELLUM_WORKFLOWS_DISPLAY_MODULE_PATH,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { BaseState } from "src/generators/base-state";
import {
  BaseCodegenError,
  NodeNotFoundError,
  NodePortNotFoundError,
} from "src/generators/errors";
import { GraphAttribute } from "src/generators/graph-attribute";
import { NodeDisplayData } from "src/generators/node-display-data";
import { WorkflowOutput } from "src/generators/workflow-output";
import {
  WorkflowDisplayData,
  WorkflowEdge,
  WorkflowNode,
} from "src/types/vellum";
import { DictEntry, isDefined } from "src/utils/typing";

export declare namespace Workflow {
  interface Args {
    /* The context for the workflow */
    workflowContext: WorkflowContext;
    /* The display data for the workflow */
    displayData?: WorkflowDisplayData;
  }
}

export class Workflow {
  public readonly workflowContext: WorkflowContext;
  private readonly displayData: WorkflowDisplayData | undefined;

  private readonly unusedNodes: Set<WorkflowNode>;
  private readonly unusedEdges: Set<WorkflowEdge>;
  constructor({ workflowContext, displayData }: Workflow.Args) {
    this.workflowContext = workflowContext;
    this.displayData = displayData;

    this.unusedNodes = new Set();
    this.unusedEdges = new Set();
  }

  private generateParentWorkflowClass(): python.Reference {
    const parentGenerics: Type[] = [];
    let customGenericsUsed = false;

    const [firstInputVariableContext] = Array.from(
      this.workflowContext.inputVariableContextsById.values()
    );
    if (firstInputVariableContext) {
      parentGenerics.push(
        python.Type.reference(
          python.reference({
            name: firstInputVariableContext.definition.name,
            modulePath: firstInputVariableContext.definition.module,
          })
        )
      );
      customGenericsUsed = true;
    } else {
      parentGenerics.push(
        python.Type.reference(
          python.reference({
            name: "BaseInputs",
            modulePath:
              this.workflowContext.sdkModulePathNames.INPUTS_MODULE_PATH,
          })
        )
      );
    }

    const [firstStateVariableContext] = Array.from(
      this.workflowContext.stateVariableContextsById.values()
    );
    if (firstStateVariableContext) {
      parentGenerics.push(
        python.Type.reference(
          python.reference({
            name: firstStateVariableContext.definition.name,
            modulePath: firstStateVariableContext.definition.module,
          })
        )
      );
      customGenericsUsed = true;
    } else {
      parentGenerics.push(
        python.Type.reference(
          new BaseState({
            workflowContext: this.workflowContext,
          })
        )
      );
    }

    const baseWorkflowClassRef = python.reference({
      name: "BaseWorkflow",
      modulePath: this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
      genericTypes: customGenericsUsed ? parentGenerics : undefined,
    });

    return baseWorkflowClassRef;
  }

  private generateOutputsClass(parentWorkflowClass: Reference): python.Class {
    const outputsClass = python.class_({
      name: OUTPUTS_CLASS_NAME,
      extends_: [
        python.reference({
          name: parentWorkflowClass.name,
          modulePath: parentWorkflowClass.modulePath,
          attribute: [OUTPUTS_CLASS_NAME],
        }),
      ],
    });

    this.workflowContext.workflowOutputContexts.forEach(
      (workflowOutputContext) => {
        outputsClass.add(
          new WorkflowOutput({
            workflowContext: this.workflowContext,
            workflowOutputContext,
          })
        );
      }
    );

    return outputsClass;
  }

  public generateWorkflowClass(): python.Class {
    const workflowClassName = this.workflowContext.workflowClassName;

    const baseWorkflowClassRef = this.generateParentWorkflowClass();

    const workflowClass = python.class_({
      name: workflowClassName,
      extends_: [baseWorkflowClassRef],
      docs: this.workflowContext.workflowClassDescription || undefined,
    });
    workflowClass.inheritReferences(baseWorkflowClassRef);

    this.addGraph(workflowClass);
    this.addUnusedGraphs(workflowClass);

    if (this.workflowContext.workflowOutputContexts.length > 0) {
      const outputsClass = this.generateOutputsClass(baseWorkflowClassRef);
      workflowClass.add(outputsClass);
    }

    return workflowClass;
  }

  public generateWorkflowDisplayClass(): python.Class {
    const workflowDisplayClassName = `${this.workflowContext.workflowClassName}Display`;

    const workflowClassRef = python.reference({
      name: this.workflowContext.workflowClassName,
      modulePath: this.getWorkflowFile().getModulePath(),
    });

    const workflowDisplayClass = python.class_({
      name: workflowDisplayClassName,
      extends_: [
        python.reference({
          name: "BaseWorkflowDisplay",
          modulePath: VELLUM_WORKFLOWS_DISPLAY_MODULE_PATH,
          genericTypes: [workflowClassRef],
        }),
      ],
    });
    workflowDisplayClass.inheritReferences(workflowClassRef);

    const entrypointNode = this.workflowContext.getEntrypointNode();
    workflowDisplayClass.add(
      python.field({
        name: "workflow_display",
        initializer: python.instantiateClass({
          classReference: python.reference({
            name: "WorkflowMetaDisplay",
            modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
          }),
          arguments_: [
            python.methodArgument({
              name: "entrypoint_node_id",
              value: python.TypeInstantiation.uuid(entrypointNode.id),
            }),
            python.methodArgument({
              name: "entrypoint_node_source_handle_id",
              value: python.TypeInstantiation.uuid(
                entrypointNode.data.sourceHandleId
              ),
            }),
            python.methodArgument({
              name: "entrypoint_node_display",
              value: new NodeDisplayData({
                workflowContext: this.workflowContext,
                nodeDisplayData: entrypointNode.displayData,
              }),
            }),
            python.methodArgument({
              name: "display_data",
              value: python.instantiateClass({
                classReference: python.reference({
                  name: "WorkflowDisplayData",
                  modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                }),
                arguments_: [
                  python.methodArgument({
                    name: "viewport",
                    value: python.instantiateClass({
                      classReference: python.reference({
                        name: "WorkflowDisplayDataViewport",
                        modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                      }),
                      arguments_: [
                        python.methodArgument({
                          name: "x",
                          value: python.TypeInstantiation.float(
                            this.displayData?.viewport.x ?? 0
                          ),
                        }),
                        python.methodArgument({
                          name: "y",
                          value: python.TypeInstantiation.float(
                            this.displayData?.viewport.y ?? 0
                          ),
                        }),
                        python.methodArgument({
                          name: "zoom",
                          value: python.TypeInstantiation.float(
                            this.displayData?.viewport.zoom ?? 0
                          ),
                        }),
                      ],
                    }),
                  }),
                ],
              }),
            }),
          ],
        }),
      })
    );

    if (this.workflowContext.inputVariableContextsById.size > 0) {
      workflowDisplayClass.add(
        python.field({
          name: "inputs_display",
          initializer: python.TypeInstantiation.dict(
            Array.from(this.workflowContext.inputVariableContextsById)
              .map(([_, inputVariableContext]) => {
                const overrideArgs: MethodArgument[] = [];

                overrideArgs.push(
                  python.methodArgument({
                    name: "id",
                    value: python.TypeInstantiation.uuid(
                      inputVariableContext.getInputVariableId()
                    ),
                  })
                );

                overrideArgs.push(
                  python.methodArgument({
                    name: "name",
                    value: python.TypeInstantiation.str(
                      // Intentionally use the raw name from the input variable data
                      // rather than the sanitized name from the input variable context
                      inputVariableContext.getRawName()
                    ),
                  })
                );

                const extensions =
                  inputVariableContext.getInputVariableData().extensions?.color;
                if (!isNil(extensions)) {
                  overrideArgs.push(
                    python.methodArgument({
                      name: "color",
                      value: python.TypeInstantiation.str(extensions),
                    })
                  );
                }
                return {
                  key: python.reference({
                    name: inputVariableContext.definition.name,
                    modulePath: inputVariableContext.definition.module,
                    attribute: [inputVariableContext.name],
                  }),
                  value: python.instantiateClass({
                    classReference: python.reference({
                      name: "WorkflowInputsDisplay",
                      modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                    }),
                    arguments_: overrideArgs,
                  }),
                };
              })
              .filter(isDefined)
          ),
        })
      );
    }

    if (this.workflowContext.stateVariableContextsById.size > 0) {
      workflowDisplayClass.add(
        python.field({
          name: "state_value_displays",
          initializer: python.TypeInstantiation.dict(
            Array.from(this.workflowContext.stateVariableContextsById)
              .map(([_, stateVariableContext]) => {
                const overrideArgs: MethodArgument[] = [];

                overrideArgs.push(
                  python.methodArgument({
                    name: "id",
                    value: python.TypeInstantiation.uuid(
                      stateVariableContext.getStateVariableId()
                    ),
                  })
                );

                overrideArgs.push(
                  python.methodArgument({
                    name: "name",
                    value: python.TypeInstantiation.str(
                      // Intentionally use the raw name from the input variable data
                      // rather than the sanitized name from the input variable context
                      stateVariableContext.getRawName()
                    ),
                  })
                );

                const extensions =
                  stateVariableContext.getStateVariableData().extensions?.color;
                if (!isNil(extensions)) {
                  overrideArgs.push(
                    python.methodArgument({
                      name: "color",
                      value: python.TypeInstantiation.str(extensions),
                    })
                  );
                }
                return {
                  key: python.reference({
                    name: stateVariableContext.definition.name,
                    modulePath: stateVariableContext.definition.module,
                    attribute: [stateVariableContext.name],
                  }),
                  value: python.instantiateClass({
                    classReference: python.reference({
                      name: "StateValueDisplay",
                      modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                    }),
                    arguments_: overrideArgs,
                  }),
                };
              })
              .filter(isDefined),
            { endWithComma: true }
          ),
        })
      );
    }

    workflowDisplayClass.add(
      python.field({
        name: "entrypoint_displays",
        initializer: python.TypeInstantiation.dict(
          this.workflowContext
            .getEntrypointNodeEdges()
            .map((edge): DictEntry | null => {
              const defaultEntrypointNodeContext =
                this.workflowContext.findNodeContext(edge.targetNodeId);

              if (!defaultEntrypointNodeContext) {
                return null;
              }

              return {
                key: python.reference({
                  name: defaultEntrypointNodeContext.nodeClassName,
                  modulePath: defaultEntrypointNodeContext.nodeModulePath,
                }),
                value: python.instantiateClass({
                  classReference: python.reference({
                    name: "EntrypointDisplay",
                    modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                  }),
                  arguments_: [
                    python.methodArgument({
                      name: "id",
                      value: python.TypeInstantiation.uuid(entrypointNode.id),
                    }),
                    python.methodArgument({
                      name: "edge_display",
                      value: python.instantiateClass({
                        classReference: python.reference({
                          name: "EdgeDisplay",
                          modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                        }),
                        arguments_: [
                          python.methodArgument({
                            name: "id",
                            value: python.TypeInstantiation.uuid(edge.id),
                          }),
                        ],
                      }),
                    }),
                  ],
                }),
              };
            })
            .filter((entry): entry is DictEntry => entry !== null)
        ),
      })
    );

    const edgeDisplayEntries: { key: AstNode; value: AstNode }[] =
      this.getEdges().reduce<{ key: AstNode; value: AstNode }[]>(
        (acc, edge) => {
          // Stable id references of edges connected to entrypoint nodes are handles separately as part of
          // `entrypoint_displays` and don't need to be taken care of here.
          const entrypointNode = this.workflowContext.getEntrypointNode();
          if (edge.sourceNodeId === entrypointNode.id) {
            return acc;
          }

          let hasError = false;

          // This is an edge case where we have a phantom port edge from a non-existent source handle
          const sourcePortId = edge.sourceHandleId;
          let sourcePortContext;
          try {
            sourcePortContext =
              this.workflowContext.getPortContextById(sourcePortId);
          } catch (e) {
            if (e instanceof NodePortNotFoundError) {
              console.warn(e.message);
            } else {
              throw e;
            }
            hasError = true;
          }

          // This is an edge case where we have a phantom edge that connects a source node to a non-existent target node
          const targetNodeId = edge.targetNodeId;
          let targetNode;
          try {
            targetNode = this.workflowContext.findNodeContext(targetNodeId);
          } catch (e) {
            if (e instanceof NodeNotFoundError) {
              console.warn(e.message);
            } else {
              throw e;
            }
            hasError = true;
          }

          if (hasError) {
            return acc;
          }

          if (sourcePortContext && targetNode) {
            const edgeDisplayEntry = {
              key: python.TypeInstantiation.tuple([
                python.reference({
                  name: sourcePortContext.nodeContext.nodeClassName,
                  modulePath: sourcePortContext.nodeContext.nodeModulePath,
                  attribute: [PORTS_CLASS_NAME, sourcePortContext.portName],
                }),
                python.reference({
                  name: targetNode.nodeClassName,
                  modulePath: targetNode.nodeModulePath,
                }),
              ]),
              value: python.instantiateClass({
                classReference: python.reference({
                  name: "EdgeDisplay",
                  modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                }),
                arguments_: [
                  python.methodArgument({
                    name: "id",
                    value: python.TypeInstantiation.uuid(edge.id),
                  }),
                  python.methodArgument({
                    name: "z_index",
                    value: !isNil(edge.display_data?.z_index)
                      ? python.TypeInstantiation.int(edge.display_data.z_index)
                      : python.TypeInstantiation.none(),
                  }),
                ],
              }),
            };

            return [...acc, edgeDisplayEntry];
          }

          return acc;
        },
        []
      );
    if (edgeDisplayEntries.length) {
      workflowDisplayClass.add(
        python.field({
          name: "edge_displays",
          initializer: python.TypeInstantiation.dict(edgeDisplayEntries),
        })
      );
    }

    workflowDisplayClass.add(
      python.field({
        name: "output_displays",
        initializer: python.TypeInstantiation.dict(
          this.workflowContext.workflowOutputContexts.map(
            (workflowOutputContext) => {
              const outputVariable = workflowOutputContext.getOutputVariable();

              return {
                key: python.reference({
                  name: this.workflowContext.workflowClassName,
                  modulePath: this.workflowContext.modulePath,
                  attribute: [OUTPUTS_CLASS_NAME, outputVariable.name],
                }),
                value: python.instantiateClass({
                  classReference: python.reference({
                    name: "WorkflowOutputDisplay",
                    modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                  }),
                  arguments_: [
                    python.methodArgument({
                      name: "id",
                      value: python.TypeInstantiation.uuid(
                        outputVariable.getOutputVariableId()
                      ),
                    }),
                    python.methodArgument({
                      name: "name",
                      value: python.TypeInstantiation.str(
                        // Intentionally use the raw name from the terminal node
                        // Rather than the sanitized name from the output context
                        outputVariable.getRawName()
                      ),
                    }),
                  ],
                }),
              };
            }
          )
        ),
      })
    );

    return workflowDisplayClass;
  }

  private getEdges(): WorkflowEdge[] {
    return this.workflowContext.workflowRawData.edges;
  }

  private getNodes(): WorkflowNode[] {
    return this.workflowContext.workflowRawData.nodes;
  }

  private getNodeIds(): Set<string> {
    return new Set(this.getNodes().map((node) => node.id));
  }

  private markUnusedNodesAndEdges(graph: GraphAttribute): void {
    const usedEdges = graph.getUsedEdges();
    const usedNodeIds = new Set<string>(
      Array.from(usedEdges).flatMap((e) => [e.sourceNodeId, e.targetNodeId])
    );

    // Also include nodes that were directly used in the graph (e.g., single-node graphs)
    const directlyUsedNodeIds = graph.getUsedNodes();
    directlyUsedNodeIds.forEach((nodeId) => usedNodeIds.add(nodeId));

    const nodeIds = this.getNodeIds();

    // Mark unused edges
    this.getEdges().forEach((edge) => {
      if (!usedEdges.has(edge)) {
        if (nodeIds.has(edge.sourceNodeId) && nodeIds.has(edge.targetNodeId)) {
          this.unusedEdges.add(edge);
        }
      }
    });

    // Mark unused nodes
    this.getNodes().forEach((node) => {
      if (!usedNodeIds.has(node.id) && node.type !== "ENTRYPOINT") {
        this.unusedNodes.add(node);
      }
    });
  }

  private addRemainingUnusedNodes(
    remainingUnusedNodes: Set<WorkflowNode>,
    unusedGraphs: (GraphAttribute | python.Reference)[]
  ): void {
    remainingUnusedNodes.forEach((node) => {
      const nodeContext = this.workflowContext.findNodeContext(node.id);
      if (!nodeContext) {
        return;
      }

      unusedGraphs.push(
        python.reference({
          name: nodeContext.nodeClassName,
          modulePath: nodeContext.nodeModulePath,
        })
      );
    });
  }

  private addGraph(workflowClass: python.Class): void {
    // Note: markUnusedNodesAndEdges() will handle determining which nodes are unused based on the generated graph

    try {
      const graph = new GraphAttribute({
        workflowContext: this.workflowContext,
      });

      // Only add graph attribute if it's not empty
      const graphMutableAst = graph.generateGraphMutableAst();
      if (graphMutableAst.type !== "empty") {
        const graphField = python.field({
          name: "graph",
          initializer: graph,
        });

        workflowClass.add(graphField);
      }

      this.markUnusedNodesAndEdges(graph);
    } catch (error) {
      if (error instanceof BaseCodegenError) {
        this.workflowContext.addError(error);
        return;
      }

      throw error;
    }
  }

  private addUnusedGraphs(workflowClass: python.Class): void {
    // Filter out edges that reference non-existent nodes
    const remainingUnusedEdges = new Set<WorkflowEdge>(this.unusedEdges);
    const remainingUnusedNodes = new Set<WorkflowNode>(this.unusedNodes);
    const remainingUnusedNodesById = Object.fromEntries(
      Array.from(remainingUnusedNodes).map((node) => [node.id, node])
    );

    if (remainingUnusedEdges.size === 0 && remainingUnusedNodes.size === 0) {
      return;
    }

    // Create a graph for each set of unused edges
    const unusedGraphs: (GraphAttribute | python.Reference)[] = [];
    while (remainingUnusedEdges.size > 0) {
      const unusedGraph = new GraphAttribute({
        workflowContext: this.workflowContext,
        unusedEdges: remainingUnusedEdges,
      });

      const processedEdges = unusedGraph.getUsedEdges();
      for (const edge of processedEdges) {
        remainingUnusedEdges.delete(edge);
        const sourceNode = remainingUnusedNodesById[edge.sourceNodeId];
        const targetNode = remainingUnusedNodesById[edge.targetNodeId];
        if (sourceNode) {
          remainingUnusedNodes.delete(sourceNode);
        }
        if (targetNode) {
          remainingUnusedNodes.delete(targetNode);
        }
      }

      unusedGraphs.push(unusedGraph);
    }

    this.addRemainingUnusedNodes(remainingUnusedNodes, unusedGraphs);

    if (unusedGraphs.length > 0) {
      const unusedGraphsField = python.field({
        name: "unused_graphs",
        initializer: python.TypeInstantiation.set(unusedGraphs),
      });

      workflowClass.add(unusedGraphsField);
    }
  }

  public getWorkflowFile(): WorkflowFile {
    return new WorkflowFile({ workflow: this });
  }

  public getWorkflowDisplayFile(): WorkflowDisplayFile {
    return new WorkflowDisplayFile({ workflow: this });
  }
}

declare namespace WorkflowFile {
  interface Args {
    workflow: Workflow;
  }
}

class WorkflowFile extends BasePersistedFile {
  private readonly workflow: Workflow;

  constructor({ workflow }: WorkflowFile.Args) {
    super({ workflowContext: workflow.workflowContext });
    this.workflow = workflow;
  }

  public getModulePath(): string[] {
    return this.workflowContext.modulePath;
  }

  protected getFileStatements(): AstNode[] {
    return [this.workflow.generateWorkflowClass()];
  }
}

declare namespace WorkflowDisplayFile {
  interface Args {
    workflow: Workflow;
  }
}

class WorkflowDisplayFile extends BasePersistedFile {
  private readonly workflow: Workflow;

  constructor({ workflow }: WorkflowDisplayFile.Args) {
    super({ workflowContext: workflow.workflowContext });

    this.workflow = workflow;
  }

  public getModulePath(): string[] {
    if (this.workflowContext.parentNode) {
      return this.workflowContext.nestedWorkflowModuleName
        ? [
            ...this.workflowContext.parentNode.getNodeDisplayModulePath(),
            this.workflowContext.nestedWorkflowModuleName,
            GENERATED_WORKFLOW_MODULE_NAME,
          ]
        : [
            ...this.workflowContext.parentNode.getNodeDisplayModulePath(),
            GENERATED_WORKFLOW_MODULE_NAME,
          ];
    } else {
      return [
        ...this.workflowContext.modulePath.slice(0, -1),
        GENERATED_DISPLAY_MODULE_NAME,
        GENERATED_WORKFLOW_MODULE_NAME,
      ];
    }
  }

  protected getFileStatements(): AstNode[] {
    return [this.workflow.generateWorkflowDisplayClass()];
  }
}
