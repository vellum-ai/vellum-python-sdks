import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export declare namespace Comment {
  interface Args {
    docs?: string;
  }
}

export class Comment extends AstNode {
  readonly docs: string | undefined;

  constructor({ docs }: Comment.Args) {
    super();
    this.docs = docs;
  }

  write(writer: Writer): void {
    if (this.docs != null) {
      this.docs.split("\n").forEach((line) => {
        writer.writeLine(`# ${line}`);
      });
    }
  }
}
