import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { Class } from "src/generators/extensions/class";
import { Writer } from "src/generators/extensions/writer";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import {
  NodePort as NodePortType,
  WorkflowDataNode,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";
import { assertUnreachable, isNilOrEmpty } from "src/utils/typing";

export declare namespace NodePorts {
  export interface Args {
    nodePorts: NodePortType[];
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    workflowContext: WorkflowContext;
  }
}

export class NodePorts extends AstNode {
  private nodeContext: BaseNodeContext<WorkflowDataNode>;
  private workflowContext: WorkflowContext;
  private astNode: AstNode | undefined = undefined;

  public constructor(args: NodePorts.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.workflowContext = args.workflowContext;
    const nodePorts = this.constructNodePorts(args.nodePorts);

    if (nodePorts) {
      this.astNode = nodePorts;
      this.inheritReferences(this.astNode);
    }
  }

  private constructNodePorts(nodePorts: NodePortType[]): AstNode | undefined {
    const baseNodeClassNameAlias =
      this.nodeContext.baseNodeClassName === this.nodeContext.nodeClassName
        ? `Base${this.nodeContext.baseNodeClassName}`
        : undefined;

    const fields: AstNode[] = [];

    nodePorts.forEach((port) => {
      const portExpression = this.generateNodePortExpression(port);
      if (portExpression) {
        fields.push(
          python.field({
            name: this.getSanitizedPortName(port),
            initializer: portExpression,
          })
        );
      }
    });

    if (isNilOrEmpty(fields)) {
      return undefined;
    }

    const clazz = new Class({
      name: "Ports",
      extends_: [
        python.reference({
          name: this.nodeContext.baseNodeClassName,
          modulePath: this.nodeContext.baseNodeClassModulePath,
          alias: baseNodeClassNameAlias,
          attribute: ["Ports"],
        }),
      ],
    });

    fields.forEach((field) => clazz.add(field));

    return clazz;
  }

  private getSanitizedPortName(port: NodePortType): string {
    const portContext = this.nodeContext.portContextsById.get(port.id);

    return portContext?.portName ?? port.name;
  }

  write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }

  private getPortAttribute(type: NodePortType["type"]): string | undefined {
    switch (type) {
      case "DEFAULT":
        return undefined;
      case "IF":
        return "on_if";
      case "ELIF":
        return "on_elif";
      default:
        return "on_else";
    }
  }

  private generateNodePortExpression(nodePort: NodePortType) {
    const attribute = this.getPortAttribute(nodePort.type);
    if (!attribute) {
      return undefined;
    }
    const descriptor = this.buildDescriptor(nodePort);
    const args = [];
    if (descriptor) {
      args.push(
        python.methodArgument({
          value: descriptor,
        })
      );
    } else if (
      isNilOrEmpty(descriptor) &&
      (attribute === "on_if" || attribute === "on_elif")
    ) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Expected IF / ELIF Ports to contain an expression",
          "WARNING"
        )
      );
      args.push(
        python.methodArgument({
          value: python.TypeInstantiation.none(),
        })
      );
    }
    return python.invokeMethod({
      methodReference: python.reference({
        name: "Port",
        modulePath: this.workflowContext.sdkModulePathNames.PORTS_MODULE_PATH,
        attribute: [attribute],
      }),
      arguments_: args,
    });
  }

  private buildDescriptor(nodePort: NodePortType): AstNode | undefined {
    let expression: WorkflowValueDescriptorType | undefined;

    switch (nodePort.type) {
      case "IF":
      case "ELIF":
        expression = nodePort.expression;
        break;
      case "ELSE":
      case "DEFAULT":
        expression = undefined;
        break;
      default:
        assertUnreachable(nodePort);
    }

    if (!expression) {
      return undefined;
    }
    return new WorkflowValueDescriptor({
      workflowValueDescriptor: expression,
      workflowContext: this.workflowContext,
      nodeContext: this.nodeContext,
    });
  }
}
