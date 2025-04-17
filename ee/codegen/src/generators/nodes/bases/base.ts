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
import { NodePorts } from "src/generators/node-port";
import { NODE_DEFAULT_ATTRIBUTES } from "src/generators/nodes/constants";
import { UuidOrString } from "src/generators/uuid-or-string";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { WorkflowProjectGenerator } from "src/project";
import {
  AdornmentNode,
  NodeDisplayComment,
  NodeDisplayData as NodeDisplayDataType,
  WorkflowDataNode,
} from "src/types/vellum";
import { isNilOrEmpty } from "src/utils/typing";

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
  protected readonly nodeAttributeNameByNodeInputId: Map<string, string>;

  private readonly errorOutputId: string | undefined;

  constructor({ workflowContext, nodeContext }: BaseNode.Args<T, V>) {
    this.workflowContext = workflowContext;
    this.nodeContext = nodeContext;
    this.nodeData = nodeContext.nodeData;

    [
      this.nodeInputsByKey,
      this.nodeInputsById,
      this.nodeAttributeNameByNodeInputId,
    ] = this.generateNodeInputs();
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
        new NodeAttributeGenerationError(
          `No input found named "${name}"`,
          "WARNING"
        )
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

  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    /**
     * This method drives how we map the key to a legacy node input to the new
     * node attribute name in the SDK.
     *
     * By default, we just pass through. However, legacy nodes can extend this
     * method to customize their specific mappings.
     */
    return nodeInputKey;
  }

  private generateNodeInputs(): [
    Map<string, NodeInput>,
    Map<string, NodeInput>,
    Map<string, string>
  ] {
    const nodeInputsByKey = new Map<string, NodeInput>();
    const nodeInputsById = new Map<string, NodeInput>();
    const nodeAttributeNameByNodeInputId = new Map<string, string>();

    if (!("inputs" in this.nodeData)) {
      return [nodeInputsByKey, nodeInputsById, nodeAttributeNameByNodeInputId];
    }

    this.nodeData.inputs.forEach((nodeInputData) => {
      try {
        const nodeInput = codegen.nodeInput({
          nodeContext: this.nodeContext,
          nodeInputData,
        });

        if (!isNilOrEmpty(nodeInput.nodeInputValuePointer.rules)) {
          nodeInputsByKey.set(nodeInputData.key, nodeInput);
          nodeInputsById.set(nodeInputData.id, nodeInput);
          const nodeAttributeName = this.getNodeAttributeNameByNodeInputKey(
            nodeInputData.key
          );
          nodeAttributeNameByNodeInputId.set(
            nodeInputData.id,
            nodeAttributeName
          );
        }
      } catch (error) {
        if (error instanceof BaseCodegenError) {
          const nodeAttributeGenerationError = new NodeAttributeGenerationError(
            `Failed to generate attribute '${this.nodeContext.nodeClassName}.inputs.${nodeInputData.key}': ${error.message}`,
            "WARNING"
          );
          this.workflowContext.addError(nodeAttributeGenerationError);
        } else {
          throw error;
        }
      }
    });

    return [nodeInputsByKey, nodeInputsById, nodeAttributeNameByNodeInputId];
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

  private generateNodeDisplayDataWithoutComment() {
    const nodeDisplayData: NodeDisplayDataType | undefined =
      this.nodeData.displayData;
    if (
      nodeDisplayData &&
      nodeDisplayData.comment &&
      nodeDisplayData.comment.expanded
    ) {
      const nodeDisplayDataWithoutComment: NodeDisplayDataType = {
        position: nodeDisplayData.position,
        width: nodeDisplayData.width,
        height: nodeDisplayData.height,
        comment: {
          expanded: nodeDisplayData.comment.expanded,
        },
      };
      return new NodeDisplayData({
        workflowContext: this.workflowContext,
        nodeDisplayData: nodeDisplayDataWithoutComment,
      });
    }
    return new NodeDisplayData({
      workflowContext: this.workflowContext,
      nodeDisplayData: this.nodeData.displayData,
    });
  }

  private getDisplayData(): python.Field {
    return python.field({
      name: "display_data",
      initializer: this.generateNodeDisplayDataWithoutComment(),
    });
  }

  protected getAdornments(): AdornmentNode[] {
    if (this.nodeData.adornments && this.nodeData.adornments.length > 0) {
      // TODO: Add validation for adornments
      return this.nodeData.adornments;
    }

    return [];
  }

  protected getNodeDecorators(): python.Decorator[] | undefined {
    const decorators: python.Decorator[] = [];
    const errorOutputId = this.getErrorOutputId();

    if (errorOutputId) {
      decorators.push(
        python.decorator({
          callable: python.invokeMethod({
            methodReference: python.reference({
              name: "TryNode",
              attribute: ["wrap"],
              modulePath:
                this.workflowContext.sdkModulePathNames.CORE_NODES_MODULE_PATH,
            }),
            arguments_: [],
          }),
        })
      );
    }

    const adornments = this.getAdornments();

    for (const adornment of adornments) {
      // TODO: remove this check when we remove errorOutputId
      if (errorOutputId && adornment.base.name === "TryNode") {
        continue;
      }

      // Filter out attributes that match their default values
      const filteredAttributes = adornment.attributes.filter((attr) =>
        this.filterAttribute(adornment.base.name, attr.name, attr.value)
      );

      if (adornment.base) {
        decorators.push(
          python.decorator({
            callable: python.invokeMethod({
              methodReference: python.reference({
                name: adornment.base.name,
                attribute: ["wrap"],
                modulePath: adornment.base.module,
              }),
              arguments_: filteredAttributes.map((attr) =>
                python.methodArgument({
                  name: attr.name,
                  value: new WorkflowValueDescriptor({
                    workflowValueDescriptor: attr.value,
                    nodeContext: this.nodeContext,
                    workflowContext: this.workflowContext,
                    iterableConfig: { endWithComma: false },
                  }),
                })
              ),
            }),
          })
        );
      }
    }

    return decorators.length > 0 ? decorators : undefined;
  }

  protected getNodePorts(): AstNode | undefined {
    if (this.nodeData.ports) {
      return new NodePorts({
        nodePorts: this.nodeData.ports,
        nodeContext: this.nodeContext,
        workflowContext: this.workflowContext,
      });
    } else {
      return undefined;
    }
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
      docs: this.generateNodeComment(),
      decorators: this.getNodeDecorators(),
    });

    try {
      this.getNodeClassBodyStatements().forEach((statement) =>
        nodeClass.add(statement)
      );
      const nodePorts = this.getNodePorts();

      if (nodePorts) {
        nodeClass.add(nodePorts);
      }
    } catch (error) {
      if (error instanceof BaseCodegenError) {
        this.workflowContext.addError(error);
      } else {
        throw error;
      }
    }

    return nodeClass;
  }

  public generateNodeDisplayClasses(): python.Class[] {
    const nodeContext = this.nodeContext;
    const decorators: python.Decorator[] = [];
    const errorOutputId = this.getErrorOutputId();

    if (errorOutputId) {
      decorators.push(
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
              // TODO: Node id and error output id are the same here for legacy reasons. Will no longer be the
              // case once we define output transformations for node adornments and could remove error output id.
              // https://linear.app/vellum/issue/APO-213/define-output-transformations-for-node-adornments
              new MethodArgument({
                name: "node_id",
                value: python.TypeInstantiation.uuid(errorOutputId),
              }),
              new MethodArgument({
                name: "error_output_id",
                value: python.TypeInstantiation.uuid(errorOutputId),
              }),
            ],
          }),
        })
      );
    }
    const adornments = this.getAdornments();

    for (const adornment of adornments) {
      // TODO: remove this check when we remove errorOutputId
      if (errorOutputId && adornment.base.name === "TryNode") {
        continue;
      }

      if (adornment.base) {
        decorators.push(
          python.decorator({
            callable: python.invokeMethod({
              methodReference: python.reference({
                name: `Base${adornment.base.name}Display`,
                attribute: ["wrap"],
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .NODE_DISPLAY_MODULE_PATH,
              }),
              // TODO: When we define output transformations, that's what we'd use here. eg, `error_output_id`.
              // https://linear.app/vellum/issue/APO-213/define-output-transformations-for-node-adornments
              arguments_: [
                new MethodArgument({
                  name: "node_id",
                  value: python.TypeInstantiation.uuid(adornment.id),
                }),
              ],
            }),
          })
        );
      }
    }

    const nodeClass = python.class_({
      name: nodeContext.nodeDisplayClassName,
      extends_: [this.getNodeDisplayBaseClass()],
      decorators: decorators.length > 0 ? decorators : undefined,
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
          const nodeAttributeName = this.nodeAttributeNameByNodeInputId.get(
            nodeInput.nodeInputData.id
          );
          return {
            key: python.TypeInstantiation.str(nodeAttributeName ?? key),
            value: new UuidOrString(nodeInput.nodeInputData.id),
          };
        })
      ),
    });
    nodeClass.add(nodeInputIdsByNameField);

    try {
      const outputDisplay = this.getOutputDisplay();
      if (outputDisplay) {
        nodeClass.add(outputDisplay);
      }
    } catch (error) {
      if (error instanceof BaseCodegenError) {
        this.workflowContext.addError(error);
      } else {
        throw error;
      }
    }

    const portDisplay = this.getPortDisplay();
    if (portDisplay) {
      nodeClass.add(portDisplay);
    }

    nodeClass.add(this.getDisplayData());

    return [nodeClass];
  }

  private getNodeComment(): NodeDisplayComment | undefined {
    return this.nodeData.displayData && "comment" in this.nodeData.displayData
      ? this.nodeData.displayData.comment
      : undefined;
  }

  private generateNodeComment(): string | undefined {
    const nodeComment = this.getNodeComment();

    if (nodeComment && nodeComment.value) {
      let comment = nodeComment.value;
      // if comment start with ", add a \ in front of it
      if (comment.startsWith('"')) {
        comment = `\\${comment}`;
      }
      // if comment end with ", add a \ in front of it
      if (comment.endsWith('"')) {
        comment = `${comment.slice(0, -1)}\\"`;
      }
      return comment;
    }
    return undefined;
  }

  private filterAttribute(
    nodeName: string,
    attributeName: string,
    attributeValue: unknown
  ): boolean {
    const nodeConfig = NODE_DEFAULT_ATTRIBUTES[nodeName];
    if (!nodeConfig) {
      return true; // Include if no config exists for this node
    }

    const attrConfig = nodeConfig[attributeName];
    if (!attrConfig) {
      return true; // Include if no config exists for this attribute
    }

    return attrConfig.defaultValue !== attributeValue; // Include if value differs from default
  }
}
