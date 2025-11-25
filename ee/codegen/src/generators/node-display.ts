import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { BaseNodeContext } from "src/context/node-context/base";
import { AstNode } from "src/generators/extensions/ast-node";
import { Class } from "src/generators/extensions/class";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Writer } from "src/generators/extensions/writer";
import {
  NodeDisplayData as NodeDisplayDataType,
  WorkflowDataNode,
} from "src/types/vellum";
import { findNodeDefinitionByBaseClassName } from "src/utils/node-definitions";
import { isNilOrEmpty } from "src/utils/typing";

export declare namespace NodeDisplay {
  export interface Args {
    nodeDisplayData: NodeDisplayDataType | undefined;
    nodeContext: BaseNodeContext<WorkflowDataNode>;
  }
}

export class NodeDisplay extends AstNode {
  private astNode: AstNode | undefined = undefined;

  public constructor(args: NodeDisplay.Args) {
    super();

    const display = this.constructNodeDisplay(
      args.nodeDisplayData,
      args.nodeContext
    );

    if (display) {
      this.astNode = display;
      this.inheritReferences(this.astNode);
    }
  }

  public isEmpty(): boolean {
    return this.astNode === undefined;
  }

  private constructNodeDisplay(
    nodeDisplayData: NodeDisplayDataType | undefined,
    nodeContext: BaseNodeContext<WorkflowDataNode>
  ): AstNode | undefined {
    const baseNodeClassNameAlias =
      nodeContext.baseNodeClassName === nodeContext.nodeClassName
        ? `Base${nodeContext.baseNodeClassName}`
        : undefined;

    const baseNodeDefinition = findNodeDefinitionByBaseClassName(
      nodeContext.baseNodeClassName
    );
    const baseDisplayDefaults: NodeDisplayDataType | undefined =
      baseNodeDefinition?.display_data;

    const fields: AstNode[] = [];

    if (
      !isNil(nodeDisplayData?.icon) &&
      nodeDisplayData.icon !== baseDisplayDefaults?.icon
    ) {
      fields.push(
        python.field({
          name: "icon",
          initializer: new StrInstantiation(nodeDisplayData.icon),
        })
      );
    }

    if (
      !isNil(nodeDisplayData?.color) &&
      nodeDisplayData.color !== baseDisplayDefaults?.color
    ) {
      fields.push(
        python.field({
          name: "color",
          initializer: new StrInstantiation(nodeDisplayData.color),
        })
      );
    }

    if (isNilOrEmpty(fields)) {
      return undefined;
    }

    const clazz = new Class({
      name: "Display",
      extends_: [
        python.reference({
          name: nodeContext.baseNodeClassName,
          modulePath: nodeContext.baseNodeClassModulePath,
          alias: baseNodeClassNameAlias,
          attribute: ["Display"],
        }),
      ],
    });

    fields.forEach((field) => clazz.add(field));

    return clazz;
  }

  write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
