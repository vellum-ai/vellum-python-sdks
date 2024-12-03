import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
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
        initializer: this.getNodeInputByName("error_source_input_id"),
      })
    );

    return bodyStatements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "label",
        initializer: python.TypeInstantiation.str(this.nodeData.data.label),
      })
    );

    return statements;
  }

  protected getOutputDisplay(): Field | undefined {
    return undefined;
  }

  getErrorOutputId(): string | undefined {
    return undefined;
  }
}
