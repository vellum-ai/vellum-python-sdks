import { AstNode } from "src/generators/extensions/ast-node";
import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";

export declare namespace SetInstantiation {
  interface Config {
    endWithComma?: boolean;
  }
}

export class SetInstantiation extends TypeInstantiation {
  private readonly values: AstNode[];
  private readonly config: SetInstantiation.Config;

  constructor(
    values: AstNode[],
    config: SetInstantiation.Config = { endWithComma: false }
  ) {
    super();
    this.values = values;
    this.config = config;
    values.forEach((value) => this.inheritReferences(value));
  }

  write(writer: Writer): void {
    writer.write("{");
    this.values.forEach((value, index) => {
      if (index > 0) {
        writer.write(", ");
      }
      value.write(writer);
      if (index === this.values.length - 1 && this.config.endWithComma) {
        writer.write(",");
      }
    });
    writer.write("}");
  }
}
