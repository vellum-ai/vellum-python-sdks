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
import { Inputs } from "src/generators/inputs";
import { NodeDisplayData } from "src/generators/node-display-data";
import { WorkflowOutput } from "src/generators/workflow-output";
import { WorkflowDisplayData, WorkflowEdge } from "src/types/vellum";
import { DictEntry, isDefined } from "src/utils/typing";

export declare namespace Workflow {
  interface Args {
    /* The name of the module that the workflow class belongs to */
    moduleName: string;
    /* The context for the workflow */
    workflowContext: WorkflowContext;
    /* The inputs for the workflow */
    inputs: Inputs;
    /* The display data for the workflow */
    displayData?: WorkflowDisplayData;
  }
}

export class Workflow {
  public readonly workflowContext: WorkflowContext;
  private readonly inputs: Inputs;
  private readonly displayData: WorkflowDisplayData | undefined;
  private readonly unusedEdges: Set<WorkflowEdge>;
  constructor({ workflowContext, inputs, displayData }: Workflow.Args) {
    this.workflowContext = workflowContext;
    this.inputs = inputs;
    this.displayData = displayData;
    this.unusedEdges = new Set();
  }

  private generateParentWorkflowClass(): python.Reference {
    let parentGenerics: Type[] | undefined;

    if (this.inputs.inputsClass) {
      let inputsClassRef: python.Reference;
      if (this.inputs.inputsClass) {
        inputsClassRef = python.reference({
          name: this.inputs.inputsClass.name,
          modulePath: this.inputs.getModulePath(),
        });
      } else {
        inputsClassRef = this.inputs.baseInputsClassReference;
      }

      const baseStateClassReference = new BaseState({
        workflowContext: this.workflowContext,
      });

      parentGenerics = [
        python.Type.reference(inputsClassRef),
        python.Type.reference(baseStateClassReference),
      ];
    }

    const baseWorkflowClassRef = python.reference({
      name: "BaseWorkflow",
      modulePath: this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
      genericTypes: parentGenerics,
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
      modulePath: this.workflowContext.modulePath,
    });

    const workflowDisplayClass = python.class_({
      name: workflowDisplayClassName,
      extends_: [
        python.reference({
          name: "VellumWorkflowDisplay",
          modulePath:
            this.workflowContext.sdkModulePathNames
              .WORKFLOWS_DISPLAY_MODULE_PATH,
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
            name: "WorkflowMetaVellumDisplayOverrides",
            modulePath:
              this.workflowContext.sdkModulePathNames.VELLUM_TYPES_MODULE_PATH,
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
                  modulePath:
                    this.workflowContext.sdkModulePathNames
                      .VELLUM_TYPES_MODULE_PATH,
                }),
                arguments_: [
                  python.methodArgument({
                    name: "viewport",
                    value: python.instantiateClass({
                      classReference: python.reference({
                        name: "WorkflowDisplayDataViewport",
                        modulePath:
                          this.workflowContext.sdkModulePathNames
                            .VELLUM_TYPES_MODULE_PATH,
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

    workflowDisplayClass.add(
      python.field({
        name: "inputs_display",
        initializer: python.TypeInstantiation.dict(
          Array.from(this.workflowContext.inputVariableContextsById)
            .map(([_, inputVariableContext]) => {
              const inputsClass = this.inputs.inputsClass;
              if (!inputsClass) {
                return;
              }

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

              const required =
                inputVariableContext.getInputVariableData().required;
              overrideArgs.push(
                python.methodArgument({
                  name: "required",
                  value: required
                    ? python.TypeInstantiation.bool(required)
                    : python.TypeInstantiation.bool(false),
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
                  name: inputsClass.name,
                  modulePath: this.inputs.getModulePath(),
                  attribute: [inputVariableContext.name],
                }),
                value: python.instantiateClass({
                  classReference: python.reference({
                    name: "WorkflowInputsVellumDisplayOverrides",
                    modulePath:
                      this.workflowContext.sdkModulePathNames
                        .VELLUM_TYPES_MODULE_PATH,
                  }),
                  arguments_: overrideArgs,
                }),
              };
            })
            .filter(isDefined)
        ),
      })
    );

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
                    name: "EntrypointVellumDisplayOverrides",
                    modulePath:
                      this.workflowContext.sdkModulePathNames
                        .VELLUM_TYPES_MODULE_PATH,
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
                          name: "EdgeVellumDisplayOverrides",
                          modulePath:
                            this.workflowContext.sdkModulePathNames
                              .VELLUM_TYPES_MODULE_PATH,
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
                  name: "EdgeVellumDisplayOverrides",
                  modulePath:
                    this.workflowContext.sdkModulePathNames
                      .VELLUM_TYPES_MODULE_PATH,
                }),
                arguments_: [
                  python.methodArgument({
                    name: "id",
                    value: python.TypeInstantiation.uuid(edge.id),
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

  private addGraph(workflowClass: python.Class): void {
    if (this.getEdges().length === 0) {
      return;
    }

    try {
      const graph = new GraphAttribute({
        workflowContext: this.workflowContext,
      });

      const graphField = python.field({
        name: "graph",
        initializer: graph,
      });

      workflowClass.add(graphField);

      // update the graph with the unused edges
      const usedEdges = graph.getUsedEdges();
      const allEdges = this.getEdges();
      allEdges.forEach((edge) => {
        if (!usedEdges.has(edge)) {
          this.unusedEdges.add(edge);
        }
      });
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
    const validUnusedEdges = new Set<WorkflowEdge>();

    this.unusedEdges.forEach((edge) => {
      if (
        this.workflowContext.globalNodeContextsByNodeId.has(
          edge.sourceNodeId
        ) &&
        this.workflowContext.globalNodeContextsByNodeId.has(edge.targetNodeId)
      ) {
        validUnusedEdges.add(edge);
      }
    });

    if (validUnusedEdges.size === 0) {
      return;
    }

    let remainingEdges = validUnusedEdges;

    // set of unused graphs
    const unusedGraphs: GraphAttribute[] = [];
    while (remainingEdges.size > 0) {
      const unusedGraph = new GraphAttribute({
        workflowContext: this.workflowContext,
        unusedEdges: remainingEdges,
      });

      const processedEdges = unusedGraph.getUsedEdges();
      remainingEdges = new Set(
        [...remainingEdges].filter((edge) => !processedEdges.has(edge))
      );

      unusedGraphs.push(unusedGraph);
    }

    const unusedGraphsField = python.field({
      name: "unused_graphs",
      initializer: python.TypeInstantiation.set(unusedGraphs),
    });

    workflowClass.add(unusedGraphsField);
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

  protected getModulePath(): string[] {
    let modulePath: string[];
    if (this.workflowContext.parentNode) {
      modulePath = [
        ...this.workflowContext.parentNode.getNodeModulePath(),
        GENERATED_WORKFLOW_MODULE_NAME,
      ];
    } else {
      modulePath = [
        this.workflowContext.moduleName,
        GENERATED_WORKFLOW_MODULE_NAME,
      ];
    }

    return modulePath;
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

  protected getModulePath(): string[] {
    let modulePath: string[];
    if (this.workflowContext.parentNode) {
      modulePath = [
        ...this.workflowContext.parentNode.getNodeDisplayModulePath(),
        GENERATED_WORKFLOW_MODULE_NAME,
      ];
    } else {
      modulePath = [
        this.workflowContext.moduleName,
        GENERATED_DISPLAY_MODULE_NAME,
        GENERATED_WORKFLOW_MODULE_NAME,
      ];
    }

    return modulePath;
  }

  protected getFileStatements(): AstNode[] {
    return [this.workflow.generateWorkflowDisplayClass()];
  }
}
