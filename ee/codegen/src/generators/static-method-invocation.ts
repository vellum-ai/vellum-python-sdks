import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import type { python } from "@fern-api/python-ast";

export class StaticMethodInvocation extends AstNode {
  private reference: python.AstNode;
  private methodName: string;
  private arguments: python.MethodArgument[];
  constructor({
    reference,
    arguments_,
    methodName,
  }: {
    reference: python.AstNode;
    arguments_: python.MethodArgument[];
    methodName: string;
  }) {
    super();
    this.reference = reference;
    this.methodName = methodName;
    this.arguments = arguments_;

    this.inheritReferences(reference);
    this.arguments.forEach((arg) => {
      this.inheritReferences(arg);
    });
  }
  write(writer: Writer) {
    this.reference.write(writer);
    writer.write(".");
    writer.write(this.methodName);
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
