import { Reference } from "src/generators/extensions/reference";
import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";

/**
 * Represents Python's UUID value instantiation.
 * This AST node writes UUID("value") to the output and adds the necessary import.
 */
export class UuidInstantiation extends TypeInstantiation {
  private readonly value: string;

  constructor(value: string) {
    super();
    this.value = value;
    this.addReference(new Reference({ name: "UUID", modulePath: ["uuid"] }));
  }

  write(writer: Writer): void {
    writer.write(`UUID("${this.value}")`);
  }
}
