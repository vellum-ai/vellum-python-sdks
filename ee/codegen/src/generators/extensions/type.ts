import { AbstractWriter } from "@fern-api/base-generator";
import { AstNode } from "@fern-api/python-ast/python";

export class PythonType extends AstNode {
  // Class that aims to replace the Type class from python-ast
  write(_: AbstractWriter) {}
}
