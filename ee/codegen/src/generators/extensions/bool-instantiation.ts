import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";

/**
 * Represents Python's boolean value instantiation.
 * This AST node writes "True" or "False" to the output based on the value.
 */
export class BoolInstantiation extends TypeInstantiation {
  private readonly value: boolean;

  constructor(value: boolean) {
    super();
    this.value = value;
  }

  write(writer: Writer): void {
    writer.write(this.value ? "True" : "False");
  }
}
