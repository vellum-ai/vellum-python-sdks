import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeContext } from "src/context/node-context/base";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { BaseNode } from "src/generators/nodes/bases";
import { WorkflowDataNode } from "src/types/vellum";

export declare namespace IdentifierFile {
  interface Args extends BasePersistedFile.Args {
    nodes: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>[];
  }
}

export class IdentifierFile extends BasePersistedFile {
  private readonly nodes: BaseNode<
    WorkflowDataNode,
    BaseNodeContext<WorkflowDataNode>
  >[];

  public constructor({ workflowContext, nodes }: IdentifierFile.Args) {
    super({ workflowContext });
    this.nodes = nodes;
  }

  protected getModulePath(): string[] {
    return [this.workflowContext.moduleName, "map"];
  }

  protected getFileStatements(): AstNode[] {
    const identifierFileMapField = python.field({
      name: "__identifiers__",
      initializer: python.TypeInstantiation.dict([
        ...this.nodes.map((node) => {
          return {
            // key: python.reference({
            //   name: node.nodeContext.nodeClassName,
            //   modulePath: node.nodeContext.nodeModulePath,
            // }),
            key: python.TypeInstantiation.str(
              node.getNodeModulePath().join(".") + "." + node.getNodeClassName()
            ),
            value: python.TypeInstantiation.uuid(node.nodeContext.getNodeId()),
          };
        }),
      ]),
    });
    this.inheritReferences(identifierFileMapField);

    return [identifierFileMapField];
  }
}
