import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/python";

import { PythonType } from "./type";

import { Writer } from "src/generators/extensions/writer";

export declare namespace Field {
  interface Args {
    name: string;
    type: python.Type | PythonType | undefined;
    initializer: AstNode | undefined;
    docs?: string;
  }
}

export class Field extends AstNode {
  name;
  type;
  initializer;
  docs;
  constructor({ name, type, initializer, docs }: Field.Args) {
    super();
    this.name = name;
    this.type = type;
    this.initializer = initializer;
    this.docs = docs;
    this.inheritReferences(this.type);
    this.inheritReferences(this.initializer);
  }
  write(writer: Writer) {
    writer.write(this.name);
    if (this.type !== undefined) {
      writer.write(": ");
      this.type.write(writer);
    }
    if (this.initializer !== undefined) {
      writer.write(" = ");
      this.initializer.write(writer);
    }
    if (this.docs != null) {
      writer.newLine();
      writer.write('"""');
      writer.newLine();
      writer.write(this.docs);
      writer.newLine();
      writer.write('"""');
    }
  }
}
