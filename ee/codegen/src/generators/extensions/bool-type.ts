import { PythonType } from "./type";
import { Writer } from "./writer";

/**
 * Represents Python's `bool` type annotation.
 * This is an inlined replacement for python.Type.bool().
 */
export class BoolType extends PythonType {
  write(writer: Writer): void {
    writer.write("bool");
  }
}
