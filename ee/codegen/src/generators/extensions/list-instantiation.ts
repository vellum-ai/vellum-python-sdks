import { AstNode } from "./ast-node";
import { Writer } from "./writer";

export declare namespace ListInstantiation {
  interface Config {
    endWithComma?: boolean;
  }
}

export class ListInstantiation extends AstNode {
  private readonly values: AstNode[];
  private readonly config: ListInstantiation.Config;

  constructor(
    values: AstNode[],
    config: ListInstantiation.Config = { endWithComma: false }
  ) {
    super();
    this.values = values;
    this.config = config;
    values.forEach((value) => this.inheritReferences(value));
  }

  write(writer: Writer): void {
    writer.write("[");
    this.values.forEach((value, index) => {
      if (index > 0) {
        writer.write(", ");
      }
      value.write(writer);
      if (index === this.values.length - 1 && this.config.endWithComma) {
        writer.write(",");
      }
    });
    writer.write("]");
  }
}
