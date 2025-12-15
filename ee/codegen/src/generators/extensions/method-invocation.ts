import { AstNode } from "./ast-node";
import { MethodArgument } from "./method-argument";
import { Reference } from "./reference";
import { Writer } from "./writer";

export declare namespace MethodInvocation {
  interface Args {
    methodReference: Reference;
    arguments_: MethodArgument[];
  }
}

export class MethodInvocation extends AstNode {
  protected reference: Reference;
  private arguments: MethodArgument[];

  constructor({ methodReference, arguments_ }: MethodInvocation.Args) {
    super();
    this.reference = methodReference;
    this.arguments = arguments_;
    this.inheritReferences(methodReference);
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
