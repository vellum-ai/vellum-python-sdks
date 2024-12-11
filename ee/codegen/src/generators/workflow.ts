import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { Reference } from "@fern-api/python-ast/Reference";
import { Type } from "@fern-api/python-ast/Type";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

import { BasePersistedFile } from "./base-persisted-file";
import { GraphAttribute } from "./graph-attribute";
import { WorkflowOutput } from "./workflow-output";

import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_WORKFLOW_MODULE_NAME,
  OUTPUTS_CLASS_NAME,
  PORTS_CLASS_NAME,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { BaseState } from "src/generators/base-state";
import { Inputs } from "src/generators/inputs";
import { NodeDisplayData } from "src/generators/node-display-data";
import {
  WorkflowDataNode,
  WorkflowDisplayData,
  WorkflowEdge,
} from "src/types/vellum";
import { getNodeId } from "src/utils/nodes";
import { isDefined } from "src/utils/typing";

export declare namespace Workflow {
  interface Args {
    /* The name of the module that the workflow class belongs to */
    moduleName: string;
    /* The context for the workflow */
    workflowContext: WorkflowContext;
    /* The inputs for the workflow */
    inputs: Inputs;
    /* The nodes in the workflow */
    nodes: WorkflowDataNode[];
    /* The display data for the workflow */
    displayData?: WorkflowDisplayData;
  }
}

export class Workflow {
  public readonly workflowContext: WorkflowContext;
  private readonly inputs: Inputs;
  private readonly nodes: WorkflowDataNode[];
  private readonly edgesByPortId: Map<string, WorkflowEdge[]>;
  private readonly entrypointNodeEdges: WorkflowEdge[];
  private readonly displayData: WorkflowDisplayData | undefined;
  private readonly entrypointNodeId: string;
  constructor({ workflowContext, inputs, nodes, displayData }: Workflow.Args) {
    this.workflowContext = workflowContext;
    this.inputs = inputs;
    this.nodes = nodes;
    this.displayData = displayData;

    const edges = this.workflowContext.workflowRawEdges;
    const { edgesByPortId, entrypointNodeEdges, entrypointNodeId } =
      this.getEdgesAndEntrypointNodeContexts({ nodes, edges });
    this.edgesByPortId = edgesByPortId;
    this.entrypointNodeEdges = entrypointNodeEdges;
    this.entrypointNodeId = entrypointNodeId;
  }

  private getEdgesAndEntrypointNodeContexts({
    nodes,
    edges,
  }: {
    nodes: WorkflowDataNode[];
    edges: WorkflowEdge[];
  }) {
    const entrypointNodeId = this.workflowContext.getEntrypointNode().id;
    const nodeIds = new Set<string>([
      ...nodes.map((node) => getNodeId(node)),
      entrypointNodeId,
    ]);
    const edgesByPortId = new Map<string, WorkflowEdge[]>();
    const entrypointNodeEdges: WorkflowEdge[] = [];

    edges.forEach((edge) => {
      // Handle edge case where there are zombie edges that point to nodes that don't exist
      if (!nodeIds.has(edge.sourceNodeId) || !nodeIds.has(edge.targetNodeId)) {
        return;
      }

      if (edge.sourceNodeId === entrypointNodeId) {
        entrypointNodeEdges.push(edge);
      }

      const portId = edge.sourceHandleId;

      const edges = edgesByPortId.get(portId) ?? [];
      edges.push(edge);
      edgesByPortId.set(portId, edges);
    });

    return {
      edgesByPortId,
      entrypointNodeEdges,
      entrypointNodeId,
    };
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
                  attribute: [inputVariableContext.getInputVariableName()],
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
          this.entrypointNodeEdges.map((edge) => {
            const defaultEntrypointNodeContext =
              this.workflowContext.getNodeContext(edge.targetNodeId);

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

          const sourcePortId = edge.sourceHandleId;
          const sourcePortContext =
            this.workflowContext.getPortContextById(sourcePortId);

          const targetNodeId = edge.targetNodeId;
          const targetNode = this.workflowContext.getNodeContext(targetNodeId);

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
              const terminalNodeData =
                workflowOutputContext.getFinalOutputNodeData();

              const edge = this.getEdges().find((edge) => {
                return (
                  edge.targetNodeId === terminalNodeData.id &&
                  edge.targetHandleId === terminalNodeData.data.targetHandleId
                );
              });

              if (!edge) {
                throw new Error(
                  `Could not find edge for terminal node ${terminalNodeData.id}`
                );
              }

              return {
                key: python.reference({
                  name: this.workflowContext.workflowClassName,
                  modulePath: this.workflowContext.modulePath,
                  attribute: [
                    OUTPUTS_CLASS_NAME,
                    workflowOutputContext.getOutputName(),
                  ],
                }),
                value: python.instantiateClass({
                  classReference: python.reference({
                    name: "WorkflowOutputVellumDisplayOverrides",
                    modulePath:
                      this.workflowContext.sdkModulePathNames
                        .VELLUM_TYPES_MODULE_PATH,
                  }),
                  arguments_: [
                    python.methodArgument({
                      name: "id",
                      value: python.TypeInstantiation.uuid(
                        terminalNodeData.data.outputId
                      ),
                    }),
                    python.methodArgument({
                      name: "node_id",
                      value: python.TypeInstantiation.uuid(terminalNodeData.id),
                    }),
                    python.methodArgument({
                      name: "node_input_id",
                      value: python.TypeInstantiation.uuid(
                        terminalNodeData.data.nodeInputId
                      ),
                    }),
                    python.methodArgument({
                      name: "name",
                      value: python.TypeInstantiation.str(
                        terminalNodeData.data.name
                      ),
                    }),
                    python.methodArgument({
                      name: "label",
                      value: python.TypeInstantiation.str(
                        terminalNodeData.data.label
                      ),
                    }),
                    python.methodArgument({
                      name: "target_handle_id",
                      value: python.TypeInstantiation.uuid(
                        terminalNodeData.data.targetHandleId
                      ),
                    }),
                    python.methodArgument({
                      name: "display_data",
                      value: new NodeDisplayData({
                        nodeDisplayData: terminalNodeData.displayData,
                        workflowContext: this.workflowContext,
                      }),
                    }),
                    python.methodArgument({
                      name: "edge_id",
                      value: python.TypeInstantiation.uuid(edge.id),
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
    return Array.from(this.edgesByPortId.values()).flat();
  }

  private addGraph(workflowClass: python.Class): void {
    if (this.nodes.length === 0) {
      return;
    }

    const graphField = python.field({
      name: "graph",
      initializer: new GraphAttribute({
        edgesByPortId: this.edgesByPortId,
        entrypointNodeEdges: this.entrypointNodeEdges,
        entrypointNodeId: this.entrypointNodeId,
        workflowContext: this.workflowContext,
      }),
    });

    workflowClass.add(graphField);
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
