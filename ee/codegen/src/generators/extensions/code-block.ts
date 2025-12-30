import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export declare namespace CodeBlock {
  type Arg = string | ((writer: Writer) => void);
}

export class CodeBlock extends AstNode {
  private arg: CodeBlock.Arg;

  constructor(arg: CodeBlock.Arg) {
    super();
    this.arg = arg;
  }

  write(writer: Writer): void {
    if (typeof this.arg === "string") {
      writer.write(this.arg);
    } else {
      this.arg(writer);
    }
  }
}
