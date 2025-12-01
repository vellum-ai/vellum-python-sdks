import { AstNode } from "./ast-node";
import { Writer } from "./writer";

/**
 * Represents Python's None value instantiation.
 * This is a simple AST node that writes "None" to the output.
 */
export class NoneInstantiation extends AstNode {
  write(writer: Writer): void {
    writer.write("None");
  }
}
