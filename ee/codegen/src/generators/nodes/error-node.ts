import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { ErrorNodeContext } from "src/context/node-context/error-node";
import { BaseNode } from "src/generators/nodes/bases/base";
import { ErrorNode as ErrorNodeType } from "src/types/vellum";

export class ErrorNode extends BaseNode<ErrorNodeType, ErrorNodeContext> {
  getNodeClassBodyStatements(): AstNode[] {
    const bodyStatements: AstNode[] = [];
    const errorSourceInputId = this.getNodeInputByName("error_source_input_id");

    if (errorSourceInputId) {
      bodyStatements.push(
        python.field({
          name: "error",
          initializer: errorSourceInputId,
        })
      );
    }

    return bodyStatements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
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
