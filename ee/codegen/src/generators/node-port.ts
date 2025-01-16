import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodePort as NodePortType } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";
import { assertUnreachable } from "src/utils/typing";

export declare namespace NodePorts {
  export interface Args {
    nodePorts: NodePortType[];
    nodeContext: GenericNodeContext;
    workflowContext: WorkflowContext;
  }
}

export class NodePorts extends AstNode {
  private nodeContext: GenericNodeContext;
  private workflowContext: WorkflowContext;
  private astNode: AstNode;

  public constructor(args: NodePorts.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.workflowContext = args.workflowContext;
    this.astNode = this.constructNodePorts(args.nodePorts);
  }

  private constructNodePorts(nodePorts: NodePortType[]): AstNode {
    const baseNodeClassNameAlias =
      this.nodeContext.baseNodeClassName === this.nodeContext.nodeClassName
        ? `Base${this.nodeContext.baseNodeClassName}`
        : undefined;

    const clazz = python.class_({
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

    nodePorts.forEach((port) => {
      clazz.add(
        python.field({
          name: toPythonSafeSnakeCase(port.name),
          initializer: this.generateNodePortExpression(port),
        })
      );
    });

    return clazz;
  }

  write(writer: Writer): void {
    this.astNode.write(writer);
  }

  private getPortAttribute(type: string): string {
    switch (type) {
      case "IF":
        return "on_if";
      case "ELIF":
        return "on_elif";
      default:
        return "on_else";
    }
  }

  private generateNodePortExpression(nodePort: NodePortType) {
    return python.invokeMethod({
      methodReference: python.reference({
        name: "Port",
        modulePath: this.workflowContext.sdkModulePathNames.PORTS_MODULE_PATH,
        attribute: [this.getPortAttribute(nodePort.type)],
      }),
      arguments_: [
        python.methodArgument({
          value: this.buildDescriptor(nodePort),
        }),
      ],
    });
  }

  // TODO: Fill this method in a fast follow
  private buildDescriptor(nodePort: NodePortType): AstNode {
    const expression = (() => {
      switch (nodePort.type) {
        case "IF":
        case "ELIF":
          return nodePort.expression;
        case "ELSE":
        case "DEFAULT":
          return undefined;
        default:
          assertUnreachable(nodePort);
      }
    })();

    if (!expression) {
      return python.TypeInstantiation.none();
    }
    switch (expression.type) {
      case "UNARY_EXPRESSION":
      case "BINARY_EXPRESSION":
      case "TERNARY_EXPRESSION":
      case "NODE_OUTPUT":
      case "INPUT_VARIABLE":
      case "CONSTANT_VALUE":
      case "WORKSPACE_SECRET":
      case "EXECUTION_COUNTER":
        return python.TypeInstantiation.none();
      default:
        assertUnreachable(expression);
    }
  }
}
