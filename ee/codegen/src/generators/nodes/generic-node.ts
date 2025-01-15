import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodeTrigger } from "src/generators/node-trigger";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { GenericNode as GenericNodeType } from "src/types/vellum";

export class GenericNode extends BaseSingleFileNode<
  GenericNodeType,
  GenericNodeContext
> {
  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    statements.push(
      new NodeTrigger({
        nodeTrigger: this.nodeData.trigger,
        nodeContext: this.nodeContext,
      })
    );
    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    return statements;
  }

  protected getOutputDisplay(): Field | undefined {
    return undefined;
  }

  protected getErrorOutputId(): string | undefined {
    return undefined;
  }
}
