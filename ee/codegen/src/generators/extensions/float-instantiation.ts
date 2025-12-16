import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";

/**
 * Represents Python's float value instantiation.
 * This AST node writes the numeric value as a float to the output.
 */
export class FloatInstantiation extends TypeInstantiation {
  private readonly value: number;

  constructor(value: number) {
    super();
    this.value = value;
  }

  write(writer: Writer): void {
    writer.write(this.value.toString());
  }
}
