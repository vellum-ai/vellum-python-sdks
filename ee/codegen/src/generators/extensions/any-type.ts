import { Reference } from "./reference";
import { PythonType } from "./type";
import { Writer } from "./writer";

/**
 * Represents Python's `Any` type annotation from the typing module.
 * This is an inlined replacement for python.Type.any().
 */
export class AnyType extends PythonType {
  constructor() {
    super();
    this.addReference(new Reference({ name: "Any", modulePath: ["typing"] }));
  }

  write(writer: Writer): void {
    writer.write("Any");
  }
}
