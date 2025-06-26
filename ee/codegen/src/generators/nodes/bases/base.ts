import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import * as codegen from "src/codegen";
import {
  PORTS_CLASS_NAME,
  VELLUM_CLIENT_MODULE_PATH,
  VELLUM_WORKFLOW_NODES_MODULE_PATH,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import {
  BaseCodegenError,
  NodeAttributeGenerationError,
} from "src/generators/errors";
import { NodeDisplayData } from "src/generators/node-display-data";
import { NodeInput } from "src/generators/node-inputs/node-input";
import { NodePorts } from "src/generators/node-port";
import { AttributeType, NODE_ATTRIBUTES } from "src/generators/nodes/constants";
import { UuidOrString } from "src/generators/uuid-or-string";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { WorkflowProjectGenerator } from "src/project";
import {
  AdornmentNode,
  NodeDisplayComment,
  NodeDisplayData as NodeDisplayDataType,
  WorkflowDataNode,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";
import { doesModulePathStartWith } from "src/utils/paths";
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

  public async persist(): Promise<void> {
    await Promise.all([
      this.getNodeFile().persist(),
      this.getNodeDisplayFile().persist(),
    ]);
  }

  public getNodeFile(): NodeImplementationFile<T, V> {
    return new NodeImplementationFile({ node: this });
  }

  public getNodeDisplayFile(): NodeDisplayFile<T, V> {
    return new NodeDisplayFile({ node: this });
  }

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
    const isVellumNode = doesModulePathStartWith(
      this.nodeContext.baseNodeClassModulePath,
      VELLUM_WORKFLOW_NODES_MODULE_PATH
    );

    const baseNodeClassName = isVellumNode
      ? this.nodeContext.baseNodeClassName
      : this.nodeContext.nodeData.base?.name ??
        this.nodeContext.baseNodeClassName;

    const baseNodeClassNameAlias =
      baseNodeClassName === this.nodeContext.nodeClassName
        ? `Base${baseNodeClassName}`
        : undefined;

    const baseNodeGenericTypes = this.getNodeBaseGenericTypes();

    return python.reference({
      name: baseNodeClassName,
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
    if (this.nodeData.ports) {
      return this.getPortDisplayFromAttribute();
    } else {
      return this.getPortDisplayFromSourceHandle();
    }
  }

  protected getPortDisplayFromAttribute(): python.Field | undefined {
    if (!this.nodeData.ports) {
      return;
    } else {
      const portDisplayOverridesDict = new Map();
      const portIds = new Set(this.nodeData.ports.map((port) => port.id));
      Array.from(this.workflowContext.portContextById.entries()).forEach(
        ([portId, context]) => {
          const isPortInCurrentNode = portIds.has(portId);
          if (isPortInCurrentNode) {
            const portDisplayOverrides = python.instantiateClass({
              classReference: python.reference({
                name: "PortDisplayOverrides",
                modulePath:
                  this.workflowContext.sdkModulePathNames
                    .NODE_DISPLAY_TYPES_MODULE_PATH,
              }),
              arguments_: [
                python.methodArgument({
                  name: "id",
                  value: python.TypeInstantiation.uuid(portId),
                }),
              ],
            });

            portDisplayOverridesDict.set(
              context.portName,
              portDisplayOverrides
            );
          }
        }
      );

      if (portDisplayOverridesDict.size > 0) {
        return python.field({
          name: "port_displays",
          initializer: python.TypeInstantiation.dict(
            Array.from(portDisplayOverridesDict.entries()).map(
              ([key, value]) => ({
                key: python.reference({
                  name: this.nodeContext.nodeClassName,
                  modulePath: this.nodeContext.nodeModulePath,
                  attribute: [PORTS_CLASS_NAME, key],
                }),
                value: value,
              })
            )
          ),
        });
      }
    }
    return;
  }

  protected getPortDisplayFromSourceHandle(): python.Field | undefined {
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
    let tryAdornmentExists = false;

    const adornments = this.getAdornments();

    for (const adornment of adornments) {
      // TODO: remove this check when we remove errorOutputId
      if (adornment.base.name === "TryNode") {
        tryAdornmentExists = true;
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
              arguments_: filteredAttributes.map((attr) => {
                const nodeConfig = NODE_ATTRIBUTES[adornment.base.name];
                const attrConfig = nodeConfig?.[attr.name];

                const attributeConfig =
                  attrConfig?.type === AttributeType.WorkflowErrorCode
                    ? {
                        lhs: python.reference({
                          name: AttributeType.WorkflowErrorCode,
                          modulePath: [
                            ...VELLUM_CLIENT_MODULE_PATH,
                            "workflows",
                            "errors",
                            "types",
                          ],
                        }),
                      }
                    : undefined;

                return python.methodArgument({
                  name: attr.name,
                  value: new WorkflowValueDescriptor({
                    workflowValueDescriptor: attr.value,
                    nodeContext: this.nodeContext,
                    workflowContext: this.workflowContext,
                    iterableConfig: { endWithComma: false },
                    attributeConfig,
                  }),
                });
              }),
            }),
          })
        );
      }
    }

    if (errorOutputId && !tryAdornmentExists) {
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

    return decorators.length > 0 ? decorators : undefined;
  }

  protected getNodePorts(): AstNode | undefined {
    if (this.nodeData.ports) {
      if (this.nodeData.ports.length === 0) {
        return undefined;
      }

      if (
        this.nodeData.ports.length === 1 &&
        this.nodeData.ports[0]?.type === "DEFAULT"
      ) {
        return undefined;
      }

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
    let tryAdornmentExists = false;

    const adornments = this.getAdornments();

    for (const adornment of adornments) {
      // TODO: remove this check when we remove errorOutputId
      if (adornment.base.name === "TryNode") {
        tryAdornmentExists = true;
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

    if (errorOutputId && !tryAdornmentExists) {
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

    const nodeClass = python.class_({
      name: nodeContext.nodeDisplayClassName,
      extends_: [this.getNodeDisplayBaseClass()],
      decorators: decorators.length > 0 ? decorators : undefined,
    });

    nodeClass.add(
      python.field({
        name: "label",
        initializer: python.TypeInstantiation.str(this.nodeContext.getNodeLabel()),
      })
    );

    nodeClass.add(
      python.field({
        name: "node_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.id),
      })
    );

    this.getNodeDisplayClassBodyStatements().forEach((statement) =>
      nodeClass.add(statement)
    );

    if (this.nodeInputsByKey.size > 0) {
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
    }

    if (this.nodeData.attributes && this.nodeData.attributes.length > 0) {
      nodeClass.add(
        python.field({
          name: "attribute_ids_by_name",
          initializer: python.TypeInstantiation.dict(
            this.nodeData.attributes.map((attribute) => {
              return {
                key: python.TypeInstantiation.str(attribute.name),
                value: python.TypeInstantiation.uuid(attribute.id),
              };
            })
          ),
        })
      );
    }

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
    attributeValue?: WorkflowValueDescriptorType | null
  ): boolean {
    if (attributeValue === undefined) {
      return true;
    }

    const nodeConfig = NODE_ATTRIBUTES[nodeName];
    const attrConfig = nodeConfig?.[attributeName];
    if (!attrConfig) {
      return true;
    }

    if (attributeValue === null) {
      return attrConfig.defaultValue !== null;
    }

    const extractedValue = this.extractConstantValue(attributeValue);
    return attrConfig.defaultValue !== extractedValue;
  }

  private extractConstantValue(
    attributeValue: WorkflowValueDescriptorType
  ): unknown {
    if (attributeValue.type !== "CONSTANT_VALUE") return attributeValue;

    const value = attributeValue.value;
    return value.type === "JSON" ? value.value : value;
  }
}

declare namespace NodeImplementationFile {
  interface Args<T extends WorkflowDataNode, V extends BaseNodeContext<T>> {
    node: BaseNode<T, V>;
  }
}

class NodeImplementationFile<
  T extends WorkflowDataNode,
  V extends BaseNodeContext<T>
> extends BasePersistedFile {
  private readonly node: BaseNode<T, V>;

  constructor({ node }: NodeImplementationFile.Args<T, V>) {
    super({ workflowContext: node.workflowContext, isInitFile: false });

    this.node = node;
  }

  protected getModulePath(): string[] {
    return this.node.getNodeModulePath();
  }

  protected getFileStatements(): AstNode[] {
    return [this.node.generateNodeClass()];
  }

  public async persist(): Promise<void> {
    await super.persist();
  }
}

declare namespace NodeDisplayFile {
  interface Args<T extends WorkflowDataNode, V extends BaseNodeContext<T>> {
    node: BaseNode<T, V>;
  }
}

class NodeDisplayFile<
  T extends WorkflowDataNode,
  V extends BaseNodeContext<T>
> extends BasePersistedFile {
  private readonly node: BaseNode<T, V>;

  constructor({ node }: NodeDisplayFile.Args<T, V>) {
    super({ workflowContext: node.workflowContext, isInitFile: false });

    this.node = node;
  }

  protected getModulePath(): string[] {
    return this.node.getNodeDisplayModulePath();
  }

  protected getFileStatements(): AstNode[] {
    return this.node.generateNodeDisplayClasses();
  }

  public async persist(): Promise<void> {
    await super.persist();
  }
}
