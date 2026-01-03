import { PythonType } from "./type";
import { Writer } from "./writer";

/**
 * Represents Python's `str` type annotation.
 * This is an inlined replacement for python.Type.str().
 */
export class StrType extends PythonType {
  write(writer: Writer): void {
    writer.write("str");
  }
}
