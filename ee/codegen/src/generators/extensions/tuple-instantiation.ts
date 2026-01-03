import { AstNode } from "src/generators/extensions/ast-node";
import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";

export declare namespace TupleInstantiation {
  interface Config {
    endWithComma?: boolean;
  }
}

export class TupleInstantiation extends TypeInstantiation {
  private readonly values: AstNode[];
  private readonly config: TupleInstantiation.Config;

  constructor(
    values: AstNode[],
    config: TupleInstantiation.Config = { endWithComma: false }
  ) {
    super();
    this.values = values;
    this.config = config;
    values.forEach((value) => this.inheritReferences(value));
  }

  write(writer: Writer): void {
    writer.write("(");
    this.values.forEach((value, index) => {
      if (index > 0) {
        writer.write(", ");
      }
      value.write(writer);
      if (
        this.values.length === 1 ||
        (index === this.values.length - 1 && this.config.endWithComma)
      ) {
        writer.write(",");
      }
    });
    writer.write(")");
  }
}
