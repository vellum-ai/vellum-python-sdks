import { AstNode } from "./ast-node";
import { Writer } from "./writer";

export declare namespace LambdaInstantiation {
  interface Args {
    body: AstNode;
  }
}

export class LambdaInstantiation extends AstNode {
  private readonly body: AstNode;

  constructor({ body }: LambdaInstantiation.Args) {
    super();
    this.body = body;
    this.inheritReferences(body);
  }

  write(writer: Writer): void {
    writer.write("lambda: ");
    this.body.write(writer);
  }
}
