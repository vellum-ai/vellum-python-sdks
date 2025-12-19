import { ErrorNodeContext } from "src/context/node-context/error-node";
import { AstNode } from "src/generators/extensions/ast-node";
import { Field } from "src/generators/extensions/field";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { BaseNode } from "src/generators/nodes/bases/base";
import { ErrorNode as ErrorNodeType } from "src/types/vellum";

export class ErrorNode extends BaseNode<ErrorNodeType, ErrorNodeContext> {
  getNodeClassBodyStatements(): AstNode[] {
    const bodyStatements: AstNode[] = [];
    const errorSourceInputId = this.getNodeInputByName("error_source_input_id");

    if (errorSourceInputId) {
      bodyStatements.push(
        new Field({
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
      new Field({
        name: "target_handle_id",
        initializer: new UuidInstantiation(this.nodeData.data.targetHandleId),
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
