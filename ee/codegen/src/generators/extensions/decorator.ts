import { AstNode } from "./ast-node";
import { Writer } from "./writer";

export declare namespace Decorator {
  interface Args {
    callable: AstNode;
  }
}

export class Decorator extends AstNode {
  private callable: AstNode;

  constructor({ callable }: Decorator.Args) {
    super();
    this.callable = callable;
    this.inheritReferences(callable);
  }

  write(writer: Writer): void {
    writer.write("@");
    this.callable.write(writer);
    writer.newLine();
  }
}
