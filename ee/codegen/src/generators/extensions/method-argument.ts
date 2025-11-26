import { AstNode } from "./ast-node";
import { Writer } from "./writer";

export declare namespace MethodArgument {
  interface Args {
    name?: string;
    value: AstNode;
  }
}

export class MethodArgument extends AstNode {
  readonly name: string | undefined;
  readonly value: AstNode;

  constructor({ name, value }: MethodArgument.Args) {
    super();
    this.name = name;
    this.value = value;
    this.inheritReferences(this.value);
  }

  write(writer: Writer): void {
    if (this.name !== undefined) {
      writer.write(this.name);
      writer.write("=");
    }
    this.value.write(writer);
  }
}
