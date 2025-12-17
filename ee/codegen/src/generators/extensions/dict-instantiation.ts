import { AstNode } from "src/generators/extensions/ast-node";
import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";

export declare namespace DictInstantiation {
  interface Config {
    endWithComma?: boolean;
  }

  interface Entry {
    key: AstNode;
    value: AstNode;
  }
}

export class DictInstantiation extends TypeInstantiation {
  private readonly entries: DictInstantiation.Entry[];
  private readonly config: DictInstantiation.Config;

  constructor(
    entries: DictInstantiation.Entry[],
    config: DictInstantiation.Config = { endWithComma: false }
  ) {
    super();
    this.entries = entries;
    this.config = config;
    entries.forEach((entry) => {
      this.inheritReferences(entry.key);
      this.inheritReferences(entry.value);
    });
  }

  write(writer: Writer): void {
    writer.write("{");
    this.entries.forEach((entry, index) => {
      if (index > 0) {
        writer.write(", ");
      }
      entry.key.write(writer);
      writer.write(": ");
      entry.value.write(writer);
      if (index === this.entries.length - 1 && this.config.endWithComma) {
        writer.write(",");
      }
    });
    writer.write("}");
  }
}
