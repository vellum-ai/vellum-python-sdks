import { isNil } from "lodash";

import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_WORKFLOW_MODULE_NAME,
  OUTPUTS_CLASS_NAME,
  PORTS_CLASS_NAME,
  VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
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
import { AstNode } from "src/generators/extensions/ast-node";
import { Class } from "src/generators/extensions/class";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { Field } from "src/generators/extensions/field";
import { FloatInstantiation } from "src/generators/extensions/float-instantiation";
import { IntInstantiation } from "src/generators/extensions/int-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { SetInstantiation } from "src/generators/extensions/set-instantiation";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { TupleInstantiation } from "src/generators/extensions/tuple-instantiation";
import { TypeReference } from "src/generators/extensions/type-reference";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { GraphAttribute } from "src/generators/graph-attribute";
import { NodeDisplayData } from "src/generators/node-display-data";
import { WorkflowOutput } from "src/generators/workflow-output";
import {
  NodeDisplayData as NodeDisplayDataType,
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

  private generateParentWorkflowClass(): Reference {
    const parentGenerics: AstNode[] = [];
    let customGenericsUsed = false;

    const [firstInputVariableContext] = Array.from(
      this.workflowContext.inputVariableContextsById.values()
    );
    if (firstInputVariableContext) {
      parentGenerics.push(
        new TypeReference(
          new Reference({
            name: firstInputVariableContext.definition.name,
            modulePath: firstInputVariableContext.definition.module,
          })
        )
      );
      customGenericsUsed = true;
    } else {
      parentGenerics.push(
        new TypeReference(
          new Reference({
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
        new TypeReference(
          new Reference({
            name: firstStateVariableContext.definition.name,
            modulePath: firstStateVariableContext.definition.module,
          })
        )
      );
      customGenericsUsed = true;
    } else {
      parentGenerics.push(
        new BaseState({
          workflowContext: this.workflowContext,
        })
      );
    }

    const baseWorkflowClassRef = new Reference({
      name: "BaseWorkflow",
      modulePath: this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
      genericTypes: customGenericsUsed ? parentGenerics : undefined,
    });

    return baseWorkflowClassRef;
  }

  private generateOutputsClass(parentWorkflowClass: Reference): Class {
    const outputsClass = new Class({
      name: OUTPUTS_CLASS_NAME,
      extends_: [
        new Reference({
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

  public generateWorkflowClass(): Class {
    const workflowClassName = this.workflowContext.workflowClassName;

    const baseWorkflowClassRef = this.generateParentWorkflowClass();

    const workflowClass = new Class({
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

  public generateWorkflowDisplayClass(): Class {
    const workflowDisplayClassName = `${this.workflowContext.workflowClassName}Display`;

    const workflowClassRef = new Reference({
      name: this.workflowContext.workflowClassName,
      modulePath: this.getWorkflowFile().getModulePath(),
    });

    const workflowDisplayClass = new Class({
      name: workflowDisplayClassName,
      extends_: [
        new Reference({
          name: "BaseWorkflowDisplay",
          modulePath: VELLUM_WORKFLOWS_DISPLAY_MODULE_PATH,
          genericTypes: [workflowClassRef],
        }),
      ],
    });
    workflowDisplayClass.inheritReferences(workflowClassRef);

    const entrypointNode = this.workflowContext.tryGetEntrypointNode();
    const entrypointNodeDisplayData = entrypointNode
      ? this.generateEntrypointNodeDisplayData(entrypointNode.displayData)
      : undefined;

    workflowDisplayClass.add(
      new Field({
        name: "workflow_display",
        initializer: new ClassInstantiation({
          classReference: new Reference({
            name: "WorkflowMetaDisplay",
            modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
          }),
          arguments_: [
            ...(entrypointNode
              ? [
                  new MethodArgument({
                    name: "entrypoint_node_id",
                    value: new UuidInstantiation(entrypointNode.id),
                  }),
                  new MethodArgument({
                    name: "entrypoint_node_source_handle_id",
                    value: new UuidInstantiation(
                      entrypointNode.data.sourceHandleId
                    ),
                  }),
                  ...(entrypointNodeDisplayData
                    ? [
                        new MethodArgument({
                          name: "entrypoint_node_display",
                          value: entrypointNodeDisplayData,
                        }),
                      ]
                    : []),
                ]
              : []),
            ...(this.displayData
              ? [
                  new MethodArgument({
                    name: "display_data",
                    value: new ClassInstantiation({
                      classReference: new Reference({
                        name: "WorkflowDisplayData",
                        modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                      }),
                      arguments_: [
                        new MethodArgument({
                          name: "viewport",
                          value: new ClassInstantiation({
                            classReference: new Reference({
                              name: "WorkflowDisplayDataViewport",
                              modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                            }),
                            arguments_: [
                              new MethodArgument({
                                name: "x",
                                value: new FloatInstantiation(
                                  this.displayData.viewport.x ?? 0
                                ),
                              }),
                              new MethodArgument({
                                name: "y",
                                value: new FloatInstantiation(
                                  this.displayData.viewport.y ?? 0
                                ),
                              }),
                              new MethodArgument({
                                name: "zoom",
                                value: new FloatInstantiation(
                                  this.displayData.viewport.zoom ?? 0
                                ),
                              }),
                            ],
                          }),
                        }),
                      ],
                    }),
                  }),
                ]
              : []),
          ],
        }),
      })
    );

    if (this.workflowContext.inputVariableContextsById.size > 0) {
      workflowDisplayClass.add(
        new Field({
          name: "inputs_display",
          initializer: new DictInstantiation(
            Array.from(this.workflowContext.inputVariableContextsById)
              .map(([_, inputVariableContext]) => {
                const overrideArgs: MethodArgument[] = [];

                overrideArgs.push(
                  new MethodArgument({
                    name: "id",
                    value: new UuidInstantiation(
                      inputVariableContext.getInputVariableId()
                    ),
                  })
                );

                overrideArgs.push(
                  new MethodArgument({
                    name: "name",
                    value: new StrInstantiation(
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
                    new MethodArgument({
                      name: "color",
                      value: new StrInstantiation(extensions),
                    })
                  );
                }
                return {
                  key: new Reference({
                    name: inputVariableContext.definition.name,
                    modulePath: inputVariableContext.definition.module,
                    attribute: [inputVariableContext.name],
                  }),
                  value: new ClassInstantiation({
                    classReference: new Reference({
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
        new Field({
          name: "state_value_displays",
          initializer: new DictInstantiation(
            Array.from(this.workflowContext.stateVariableContextsById)
              .map(([_, stateVariableContext]) => {
                const overrideArgs: MethodArgument[] = [];

                overrideArgs.push(
                  new MethodArgument({
                    name: "id",
                    value: new UuidInstantiation(
                      stateVariableContext.getStateVariableId()
                    ),
                  })
                );

                overrideArgs.push(
                  new MethodArgument({
                    name: "name",
                    value: new StrInstantiation(
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
                    new MethodArgument({
                      name: "color",
                      value: new StrInstantiation(extensions),
                    })
                  );
                }
                return {
                  key: new Reference({
                    name: stateVariableContext.definition.name,
                    modulePath: stateVariableContext.definition.module,
                    attribute: [stateVariableContext.name],
                  }),
                  value: new ClassInstantiation({
                    classReference: new Reference({
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
      new Field({
        name: "entrypoint_displays",
        initializer: new DictInstantiation(
          this.workflowContext
            .getTriggerEdges()
            .map((edge): DictEntry | null => {
              const defaultEntrypointNodeContext =
                this.workflowContext.findNodeContext(edge.targetNodeId);

              if (!defaultEntrypointNodeContext) {
                return null;
              }

              return {
                key: new Reference({
                  name: defaultEntrypointNodeContext.nodeClassName,
                  modulePath: defaultEntrypointNodeContext.nodeModulePath,
                }),
                value: new ClassInstantiation({
                  classReference: new Reference({
                    name: "EntrypointDisplay",
                    modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                  }),
                  arguments_: [
                    new MethodArgument({
                      name: "id",
                      value: new UuidInstantiation(
                        // Use trigger ID when no entrypoint node exists (IntegrationTrigger workflows)
                        entrypointNode?.id ?? edge.sourceNodeId
                      ),
                    }),
                    new MethodArgument({
                      name: "edge_display",
                      value: new ClassInstantiation({
                        classReference: new Reference({
                          name: "EdgeDisplay",
                          modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                        }),
                        arguments_: [
                          new MethodArgument({
                            name: "id",
                            value: new UuidInstantiation(edge.id),
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
          // Stable id references of edges connected to entrypoint nodes or triggers are handled separately as part of
          // `entrypoint_displays` and don't need to be taken care of here.
          const entrypointNode = this.workflowContext.tryGetEntrypointNode();
          const triggers = this.workflowContext.triggers;
          const isTriggerSource = triggers?.some(
            (t) => t.id === edge.sourceNodeId
          );
          if (
            (entrypointNode && edge.sourceNodeId === entrypointNode.id) ||
            isTriggerSource
          ) {
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
            const zIndex = edge.display_data?.z_index;
            const edgeDisplayEntry = {
              key: new TupleInstantiation([
                new Reference({
                  name: sourcePortContext.nodeContext.nodeClassName,
                  modulePath: sourcePortContext.nodeContext.nodeModulePath,
                  attribute: [PORTS_CLASS_NAME, sourcePortContext.portName],
                }),
                new Reference({
                  name: targetNode.nodeClassName,
                  modulePath: targetNode.nodeModulePath,
                }),
              ]),
              value: new ClassInstantiation({
                classReference: new Reference({
                  name: "EdgeDisplay",
                  modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                }),
                arguments_: [
                  new MethodArgument({
                    name: "id",
                    value: new UuidInstantiation(edge.id),
                  }),
                  new MethodArgument({
                    name: "z_index",
                    value: !isNil(zIndex)
                      ? new IntInstantiation(zIndex)
                      : new NoneInstantiation(),
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
        new Field({
          name: "edge_displays",
          initializer: new DictInstantiation(edgeDisplayEntries),
        })
      );
    }

    workflowDisplayClass.add(
      new Field({
        name: "output_displays",
        initializer: new DictInstantiation(
          this.workflowContext.workflowOutputContexts
            .map((workflowOutputContext) => {
              const outputVariable = workflowOutputContext.getOutputVariable();
              if (!outputVariable) {
                return undefined;
              }

              return {
                key: new Reference({
                  name: this.workflowContext.workflowClassName,
                  modulePath: this.workflowContext.modulePath,
                  attribute: [OUTPUTS_CLASS_NAME, outputVariable.name],
                }),
                value: new ClassInstantiation({
                  classReference: new Reference({
                    name: "WorkflowOutputDisplay",
                    modulePath: VELLUM_WORKFLOWS_DISPLAY_BASE_PATH,
                  }),
                  arguments_: [
                    new MethodArgument({
                      name: "id",
                      value: new UuidInstantiation(
                        outputVariable.getOutputVariableId()
                      ),
                    }),
                    new MethodArgument({
                      name: "name",
                      value: new StrInstantiation(
                        // Intentionally use the raw name from the terminal node
                        // Rather than the sanitized name from the output context
                        outputVariable.getRawName()
                      ),
                    }),
                  ],
                }),
              };
            })
            .filter((entry) => entry !== undefined)
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
    unusedGraphs: (GraphAttribute | Reference)[]
  ): void {
    remainingUnusedNodes.forEach((node) => {
      const nodeContext = this.workflowContext.findNodeContext(node.id);
      if (!nodeContext) {
        return;
      }

      unusedGraphs.push(
        new Reference({
          name: nodeContext.nodeClassName,
          modulePath: nodeContext.nodeModulePath,
        })
      );
    });
  }

  private addGraph(workflowClass: Class): void {
    // Note: markUnusedNodesAndEdges() will handle determining which nodes are unused based on the generated graph

    try {
      const graph = new GraphAttribute({
        workflowContext: this.workflowContext,
      });

      // Only add graph attribute if it's not empty
      const graphMutableAst = graph.generateGraphMutableAst();
      if (graphMutableAst.type !== "empty") {
        const graphField = new Field({
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

  private addUnusedGraphs(workflowClass: Class): void {
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
    const unusedGraphs: (GraphAttribute | Reference)[] = [];
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
      // Flatten any GraphAttributes that contain sets into their individual elements
      const flattenedUnusedGraphs: AstNode[] = [];
      for (const graph of unusedGraphs) {
        if (graph instanceof GraphAttribute) {
          const astNodes = graph.getAstNodesForUnusedGraphs();
          flattenedUnusedGraphs.push(...astNodes);
        } else {
          flattenedUnusedGraphs.push(graph);
        }
      }

      const unusedGraphsField = new Field({
        name: "unused_graphs",
        initializer: new SetInstantiation(flattenedUnusedGraphs),
      });

      workflowClass.add(unusedGraphsField);
    }
  }

  /**
   * Generates the NodeDisplayData for the entrypoint node.
   * Unlike regular nodes which store position in BaseNode.Display,
   * the entrypoint node stores position in WorkflowMetaDisplay.entrypoint_node_display.
   */
  private generateEntrypointNodeDisplayData(
    displayData: NodeDisplayDataType | undefined
  ): ClassInstantiation | undefined {
    const args: MethodArgument[] = [];

    // Always include position for entrypoint nodes since they don't have a BaseNode.Display class
    args.push(
      new MethodArgument({
        name: "position",
        value: new ClassInstantiation({
          classReference: new Reference({
            name: "NodeDisplayPosition",
            modulePath: VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
          }),
          arguments_: [
            new MethodArgument({
              name: "x",
              value: new FloatInstantiation(displayData?.position?.x ?? 0),
            }),
            new MethodArgument({
              name: "y",
              value: new FloatInstantiation(displayData?.position?.y ?? 0),
            }),
          ],
        }),
      })
    );

    if (!isNil(displayData?.z_index)) {
      args.push(
        new MethodArgument({
          name: "z_index",
          value: new IntInstantiation(displayData.z_index),
        })
      );
    }

    if (!isNil(displayData?.width)) {
      args.push(
        new MethodArgument({
          name: "width",
          value: new IntInstantiation(displayData.width),
        })
      );
    }

    if (!isNil(displayData?.height)) {
      args.push(
        new MethodArgument({
          name: "height",
          value: new IntInstantiation(displayData.height),
        })
      );
    }

    return new ClassInstantiation({
      classReference: new Reference({
        name: "NodeDisplayData",
        modulePath: VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
      }),
      arguments_: args,
    });
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
