import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";

/**
 * Represents Python's None value instantiation.
 * This is a simple AST node that writes "None" to the output.
 */
export class NoneInstantiation extends TypeInstantiation {
  write(writer: Writer): void {
    writer.write("None");
  }
}
