import { AstNode } from "./ast-node";
import { Reference } from "./reference";
import { Writer } from "./writer";

/**
 * TypeReference is an inlined replacement for python.Type.reference().
 * It wraps a Reference and writes it directly, inheriting its references.
 *
 * This is part of the effort to eject from the @fern-api/python-ast package.
 */
export class TypeReference extends AstNode {
  private readonly value: Reference;

  constructor(value: Reference) {
    super();
    this.value = value;
    this.addReference(value);
  }

  write(writer: Writer): void {
    this.value.write(writer);
  }
}
