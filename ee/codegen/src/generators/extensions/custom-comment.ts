import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

export declare namespace CustomComment {
  interface Args {
    docs: string;
  }
}

export class CustomComment extends AstNode {
  private readonly docs: string;

  constructor({ docs }: CustomComment.Args) {
    super();
    this.docs = docs;
  }

  public write(writer: Writer): void {
    if (this.docs.includes("\n")) {
      // For multi-line comments
      writer.write('"""');
      writer.newLine();

      const lines = this.docs.split("\n");

      lines.forEach((line, index) => {
        writer.write(line);
        if (index < lines.length - 1) {
          writer.newLine();
        }
      });

      writer.newLine();
      writer.write('"""');
    } else {
      // For single-line comments
      let escapedDocs = this.docs;

      // Handle quotes at the beginning
      if (this.docs.startsWith('"')) {
        escapedDocs = "\\" + escapedDocs;
      }

      // Handle quotes at the end
      if (this.docs.endsWith('"')) {
        escapedDocs = escapedDocs.slice(0, -1) + '\\"';
      }

      // Write the triple-quoted string without any extra spaces
      writer.write('"""');
      writer.write(escapedDocs);
      writer.write('"""');
    }
  }
}
