import { AstNode } from "./ast-node";
import { Writer } from "./writer";

export declare namespace StrInstantiation {
  interface Config {
    multiline?: boolean;
    startOnNewLine?: boolean;
    endWithNewLine?: boolean;
  }
}

export class StrInstantiation extends AstNode {
  private readonly value: string;
  private readonly config: StrInstantiation.Config;

  constructor(
    value: string,
    config: StrInstantiation.Config = {
      multiline: false,
      startOnNewLine: false,
      endWithNewLine: false,
    }
  ) {
    super();
    this.value = value;
    this.config = config;
  }

  write(writer: Writer): void {
    if (this.config.multiline) {
      const { startOnNewLine, endWithNewLine } = this.config;
      this.writeStringWithTripleQuotes({
        writer,
        value: this.value,
        startOnNewLine,
        endWithNewLine,
      });
    } else {
      writer.write(`"${this.escapeString(this.value)}"`);
    }
  }

  private writeStringWithTripleQuotes({
    writer,
    value,
    startOnNewLine,
    endWithNewLine,
  }: {
    writer: Writer;
    value: string;
    startOnNewLine?: boolean;
    endWithNewLine?: boolean;
  }): void {
    writer.write('"""');
    const lines = value.split("\n");
    if (lines.length <= 1) {
      writer.write(this.escapeString(lines[0] ?? ""));
      writer.write('"""');
      return;
    }
    if (startOnNewLine) {
      writer.writeNoIndent("\\\n");
    }
    lines.forEach((line, idx) => {
      writer.writeNoIndent(this.escapeString(line));
      if (idx === lines.length - 1) {
        if (endWithNewLine) {
          writer.writeNoIndent("\\\n");
        }
      } else {
        writer.writeNoIndent("\n");
      }
    });
    writer.writeNoIndent('"""');
  }

  private escapeString(input: string): string {
    const pattern = /(?<!\\)(["'\\\t\n\r])/g;
    const replacements: Record<string, string> = {
      '"': '\\"',
      "'": "\\'",
      "\\": "\\\\",
      "\t": "\\t",
      "\n": "\\n",
      "\r": "\\r",
    };
    return input.replace(pattern, (char) => replacements[char] ?? char);
  }
}
