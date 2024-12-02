import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { ErrorNodeContext } from "src/context/node-context/error-node";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { ErrorNode as ErrorNodeType } from "src/types/vellum";

export class ErrorNode extends BaseSingleFileNode<
  ErrorNodeType,
  ErrorNodeContext
> {
  baseNodeClassName = "ErrorNode";
  baseNodeDisplayClassName = "BaseErrorNodeDisplay";

  getNodeClassBodyStatements(): AstNode[] {
    const bodyStatements: AstNode[] = [];
    bodyStatements.push(
      python.field({
        name: "error",
        initializer: this.getNodeInputByName("error_source"),
      })
    );

    return bodyStatements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    return statements;
  }

  getErrorOutputId(): string | undefined {
    return undefined;
  }
}
