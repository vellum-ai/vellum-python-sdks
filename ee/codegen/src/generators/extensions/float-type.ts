import { PythonType } from "./type";
import { Writer } from "./writer";

/**
 * Represents Python's `float` type annotation.
 * This is an inlined replacement for python.Type.float().
 */
export class FloatType extends PythonType {
  write(writer: Writer): void {
    writer.write("float");
  }
}
