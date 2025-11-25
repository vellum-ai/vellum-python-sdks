import { MethodArgument } from "@fern-api/python-ast/MethodArgument";

import { AstNode } from "./ast-node";
import { Reference } from "./reference";
import { Writer } from "./writer";

export declare namespace ClassInstantiation {
  interface Args {
    classReference: Reference;
    arguments_: MethodArgument[];
  }
}

export class ClassInstantiation extends AstNode {
  protected reference: Reference;
  private arguments: MethodArgument[];

  constructor({ classReference, arguments_ }: ClassInstantiation.Args) {
    super();
    this.reference = classReference;
    this.arguments = arguments_;
    this.inheritReferences(classReference);
    this.arguments.forEach((arg) => {
      this.inheritReferences(arg);
    });
  }

  write(writer: Writer): void {
    this.reference.write(writer);
    writer.write("(");
    this.arguments.forEach((arg, idx) => {
      arg.write(writer);
      if (idx < this.arguments.length - 1) {
        writer.write(", ");
      }
    });
    writer.write(")");
  }
}
