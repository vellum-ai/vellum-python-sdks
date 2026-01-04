import { Reference } from "./reference";
import { PythonType } from "./type";
import { Writer } from "./writer";

/**
 * TypeReference is an inlined replacement for python.Type.reference().
 * It wraps a Reference and writes it directly, inheriting its references.
 */
export class TypeReference extends PythonType {
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
