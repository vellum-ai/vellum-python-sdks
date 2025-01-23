import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import * as codegen from "src/codegen";
import { PORTS_CLASS_NAME } from "src/constants";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import {
  BaseCodegenError,
  NodeAttributeGenerationError,
} from "src/generators/errors";
import { NodeDisplayData } from "src/generators/node-display-data";
import { NodeInput } from "src/generators/node-inputs/node-input";
import { UuidOrString } from "src/generators/uuid-or-string";
import { WorkflowProjectGenerator } from "src/project";
import { WorkflowDataNode } from "src/types/vellum";

export declare namespace BaseNode {
  interface Args<T extends WorkflowDataNode, V extends BaseNodeContext<T>> {
    workflowContext: WorkflowContext;
    nodeContext: V;
  }
}

export abstract class BaseNode<
  T extends WorkflowDataNode,
  V extends BaseNodeContext<T>
> {
  public readonly workflowContext: WorkflowContext;
  public readonly nodeData: T;
  public readonly nodeContext: V;

  protected readonly nodeInputsByKey: Map<string, NodeInput>;
  protected readonly nodeInputsById: Map<string, NodeInput>;

  private readonly errorOutputId: string | undefined;

  constructor({ workflowContext, nodeContext }: BaseNode.Args<T, V>) {
    this.workflowContext = workflowContext;
    this.nodeContext = nodeContext;
    this.nodeData = nodeContext.nodeData;

    [this.nodeInputsByKey, this.nodeInputsById] = this.generateNodeInputs();
    this.errorOutputId = this.getErrorOutputId();
  }

  public abstract persist(): Promise<void>;

  protected abstract getNodeClassBodyStatements(): AstNode[];

  protected abstract getNodeDisplayClassBodyStatements(): AstNode[];

  // Override to specify a custom output display
  protected abstract getOutputDisplay(): python.Field | undefined;

  // If the node supports the Reject on Error toggle, then implement this to return
  // the error_output_id from this.nodeData. If returned, a @TryNode decorator will be
  // added to the node class.
  protected abstract getErrorOutputId(): string | undefined;

  // Override if the node implementation's base class needs to include generic types
  protected getNodeBaseGenericTypes(): AstNode[] | undefined {
    return undefined;
  }

  protected getNodeBaseClass(): python.Reference {
    const baseNodeClassNameAlias =
      this.nodeContext.baseNodeClassName === this.nodeContext.nodeClassName
        ? `Base${this.nodeContext.baseNodeClassName}`
        : undefined;

    const baseNodeGenericTypes = this.getNodeBaseGenericTypes();

    return python.reference({
      name: this.nodeContext.baseNodeClassName,
      modulePath: this.nodeContext.baseNodeClassModulePath,
      genericTypes: baseNodeGenericTypes,
      alias: baseNodeClassNameAlias,
    });
  }

  protected getNodeDisplayBaseClass(): python.Reference {
    return python.reference({
      name: this.nodeContext.baseNodeDisplayClassName,
      modulePath: this.nodeContext.baseNodeDisplayClassModulePath,
      genericTypes: [
        python.reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
        }),
      ],
    });
  }

  /* Override if the node implementation needs to generate nested workflows */
  protected generateNestedWorkflowContexts(): Map<string, WorkflowContext> {
    return new Map();
  }

  /* Override if the node implementation needs to generate nested workflows */
  protected generateNestedProjectsByName(): Map<
    string,
    WorkflowProjectGenerator
  > {
    return new Map();
  }

  protected findNodeInputByName(name: string): NodeInput | undefined {
    return this.nodeInputsByKey.get(name);
  }

  protected getNodeInputByName(name: string): NodeInput | undefined {
    const nodeInput = this.findNodeInputByName(name);
    if (!nodeInput) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(`No input found named "${name}"`)
      );
    }

    return nodeInput;
  }

  public getNodeClassName() {
    return this.nodeContext.nodeClassName;
  }

  public getNodeModulePath() {
    return this.nodeContext.nodeModulePath;
  }

  public getNodeDisplayClassName() {
    return this.nodeContext.nodeDisplayClassName;
  }

  public getNodeDisplayModulePath() {
    return this.nodeContext.nodeDisplayModulePath;
  }

  private generateNodeInputs(): [
    Map<string, NodeInput>,
    Map<string, NodeInput>
  ] {
    const nodeInputsByKey = new Map<string, NodeInput>();
    const nodeInputsById = new Map<string, NodeInput>();

    if (!("inputs" in this.nodeData)) {
      return [nodeInputsByKey, nodeInputsById];
    }

    this.nodeData.inputs.forEach((nodeInputData) => {
      try {
        const nodeInput = codegen.nodeInput({
          workflowContext: this.workflowContext,
          nodeInputData,
        });

        nodeInputsByKey.set(nodeInputData.key, nodeInput);
        nodeInputsById.set(nodeInputData.id, nodeInput);
      } catch (error) {
        if (error instanceof BaseCodegenError) {
          const nodeAttributeGenerationError = new NodeAttributeGenerationError(
            `Failed to generate attribute '${this.nodeContext.nodeClassName}.inputs.${nodeInputData.key}': ${error.message}`
          );
          this.workflowContext.addError(nodeAttributeGenerationError);
        } else {
          throw error;
        }
      }
    });

    return [nodeInputsByKey, nodeInputsById];
  }

  protected getPortDisplay(): python.Field | undefined {
    if (
      !("data" in this.nodeData) ||
      !("sourceHandleId" in this.nodeData.data)
    ) {
      return;
    }

    return python.field({
      name: "port_displays",
      initializer: python.TypeInstantiation.dict([
        {
          key: python.reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [PORTS_CLASS_NAME, "default"],
          }),
          value: python.instantiateClass({
            classReference: python.reference({
              name: "PortDisplayOverrides",
              modulePath:
                this.workflowContext.sdkModulePathNames
                  .NODE_DISPLAY_TYPES_MODULE_PATH,
            }),
            arguments_: [
              python.methodArgument({
                name: "id",
                value: python.TypeInstantiation.uuid(
                  this.nodeData.data.sourceHandleId
                ),
              }),
            ],
          }),
        },
      ]),
    });
  }

  private getDisplayData(): python.Field {
    return python.field({
      name: "display_data",
      initializer: new NodeDisplayData({
        workflowContext: this.workflowContext,
        nodeDisplayData: this.nodeData.displayData,
      }),
    });
  }

  protected getNodeDecorators(): python.Decorator[] | undefined {
    return this.errorOutputId
      ? [
          python.decorator({
            callable: python.invokeMethod({
              methodReference: python.reference({
                name: "TryNode",
                attribute: ["wrap"],
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .CORE_NODES_MODULE_PATH,
              }),
              arguments_: [],
            }),
          }),
        ]
      : undefined;
  }

  public generateNodeClass(): python.Class {
    const nodeContext = this.nodeContext;

    let nodeBaseClass: python.Reference = this.getNodeBaseClass();
    if (nodeBaseClass.name === nodeContext.nodeClassName) {
      nodeBaseClass = python.reference({
        name: nodeBaseClass.name,
        modulePath: nodeBaseClass.modulePath,
        genericTypes: nodeBaseClass.genericTypes,
        alias: `Base${nodeBaseClass.name}`,
        attribute: nodeBaseClass.attribute,
      });
    }

    const nodeClass = python.class_({
      name: nodeContext.nodeClassName,
      extends_: [nodeBaseClass],
      decorators: this.getNodeDecorators(),
    });

    this.getNodeClassBodyStatements().forEach((statement) =>
      nodeClass.add(statement)
    );

    return nodeClass;
  }

  public generateNodeDisplayClasses(): python.Class[] {
    const nodeContext = this.nodeContext;
    const errorOutputId = this.getErrorOutputId();

    const nodeClass = python.class_({
      name: nodeContext.nodeDisplayClassName,
      extends_: [this.getNodeDisplayBaseClass()],
      decorators: errorOutputId
        ? [
            python.decorator({
              callable: python.invokeMethod({
                methodReference: python.reference({
                  name: "BaseTryNodeDisplay",
                  attribute: ["wrap"],
                  modulePath:
                    this.workflowContext.sdkModulePathNames
                      .NODE_DISPLAY_MODULE_PATH,
                }),
                arguments_: [
                  new MethodArgument({
                    name: "error_output_id",
                    value: python.TypeInstantiation.uuid(errorOutputId),
                  }),
                ],
              }),
            }),
          ]
        : undefined,
    });

    this.getNodeDisplayClassBodyStatements().forEach((statement) =>
      nodeClass.add(statement)
    );

    const nodeInputIdsByNameField = python.field({
      name: "node_input_ids_by_name",
      initializer: python.TypeInstantiation.dict(
        Array.from(this.nodeInputsByKey).map<{
          key: AstNode;
          value: AstNode;
        }>(([key, nodeInput]) => {
          return {
            key: python.TypeInstantiation.str(key),
            value: new UuidOrString(nodeInput.nodeInputData.id),
          };
        })
      ),
    });
    nodeClass.add(nodeInputIdsByNameField);

    const outputDisplay = this.getOutputDisplay();
    if (outputDisplay) {
      nodeClass.add(outputDisplay);
    }

    const portDisplay = this.getPortDisplay();
    if (portDisplay) {
      nodeClass.add(portDisplay);
    }

    nodeClass.add(this.getDisplayData());

    return [nodeClass];
  }
}
