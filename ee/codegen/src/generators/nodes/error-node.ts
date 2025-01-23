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
        name: "name",
        initializer: python.TypeInstantiation.str(this.nodeData.data.name),
      })
    );

    statements.push(
      python.field({
        name: "node_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.id),
      })
    );
    statements.push(
      python.field({
        name: "label",
        initializer: python.TypeInstantiation.str(this.nodeData.data.label),
      })
    );

    statements.push(
      python.field({
        name: "error_output_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.errorOutputId
        ),
      })
    );

    statements.push(
      python.field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
      })
    );

    statements.push(
      python.field({
        name: "error_inputs_by_name",
        initializer: python.TypeInstantiation.dict(
          Array.from(this.nodeInputsByKey.entries()).map(([key, value]) => ({
            key: python.TypeInstantiation.str(key),
            value: value,
          }))
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
