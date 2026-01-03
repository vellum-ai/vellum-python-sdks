import { PythonType } from "./type";
import { Writer } from "./writer";

/**
 * Represents Python's `None` type annotation.
 * This is an inlined replacement for python.Type.none().
 */
export class NoneType extends PythonType {
  write(writer: Writer): void {
    writer.write("None");
  }
}
