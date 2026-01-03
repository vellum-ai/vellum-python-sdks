import { PythonType } from "./type";
import { Writer } from "./writer";

/**
 * Represents Python's `int` type annotation.
 * This is an inlined replacement for python.Type.int().
 */
export class IntType extends PythonType {
  write(writer: Writer): void {
    writer.write("int");
  }
}
