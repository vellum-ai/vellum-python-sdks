import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";

import { NoteNodeContext } from "src/context/node-context/note-node";
import { AstNode } from "src/generators/extensions/ast-node";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Json } from "src/generators/json";
import { BaseNode } from "src/generators/nodes/bases/base";
import { NoteNode as NoteNodeType } from "src/types/vellum";

export class NoteNode extends BaseNode<NoteNodeType, NoteNodeContext> {
  getNodeClassBodyStatements(): AstNode[] {
    // Note Nodes intentionally have no body statements, but Python requires at least one statement.
    return [python.codeBlock("pass")];
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "text",
        initializer: new StrInstantiation(this.nodeData.data.text ?? ""),
      })
    );

    const styleValue = this.nodeData.data.style
      ? new Json(this.nodeData.data.style)
      : python.TypeInstantiation.none();

    statements.push(
      python.field({
        name: "style",
        initializer: styleValue,
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
