import { python } from "@fern-api/python-ast";
import { Decorator } from "@fern-api/python-ast/Decorator";
import { Reference } from "@fern-api/python-ast/Reference";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { Field } from "./field";

export declare namespace Class {
  interface Args {
    name: string;
    docs?: string;
    extends_?: Reference[];
    decorators?: Decorator[];
  }
}

export class Class extends AstNode {
  readonly name: string;
  readonly extends_: Reference[];
  readonly decorators: Decorator[];
  readonly fields: (python.Field | Field)[] = [];
  readonly docs?: string;
  private statements: AstNode[] = [];
  constructor({ docs, name, extends_, decorators }: Class.Args) {
    super();
    this.name = name;
    this.extends_ = extends_ ?? [];
    this.decorators = decorators ?? [];
    this.docs = docs;
    this.extends_.forEach((parentClassReference) => {
      this.inheritReferences(parentClassReference);
    });
    this.decorators.forEach((decorator) => {
      this.inheritReferences(decorator);
    });
  }
  write(writer: Writer) {
    this.decorators.forEach((decorator) => {
      decorator.write(writer);
    });
    writer.write(`class ${this.name}`);
    if (this.extends_.length > 0) {
      writer.write("(");
      this.extends_.forEach((parentClassReference, index) => {
        if (index > 0) {
          writer.write(", ");
        }
        parentClassReference.write(writer);
      });
      writer.write(")");
    }
    writer.write(":");
    writer.newLine();
    writer.indent();
    if (this.docs != null) {
      writer.write('"""');
      writer.write(this.docs);
      writer.write('"""');
    }
    writer.writeNewLineIfLastLineNot();
    this.fields.forEach((field) => {
      field.write(writer);
      writer.writeNewLineIfLastLineNot();
    });
    writer.dedent();
    writer.indent();
    if (this.statements.length) {
      this.writeStatements({ writer });
    } else {
      writer.write("pass");
    }
    writer.dedent();
  }
  add(statement: AstNode) {
    this.statements.push(statement);
    this.inheritReferences(statement);
  }
  writeStatements({ writer }: { writer: Writer }) {
    this.statements.forEach((statement) => {
      statement.write(writer);
      writer.writeNewLineIfLastLineNot();
    });
  }
  addField(field: python.Field | Field) {
    this.add(field);
  }
}
