import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { ModulePath } from "@fern-api/python-ast/core/types";

import { Writer } from "src/generators/extensions/writer";

export declare namespace StarImport {
  interface Args {
    modulePath: ModulePath;
  }
}

export class StarImport extends AstNode {
  readonly name: string;
  readonly modulePath: ModulePath;

  constructor({ modulePath }: StarImport.Args) {
    super();
    this.name = "*";
    this.modulePath = modulePath ?? [];
    this.references.push(this);
  }

  write(_: Writer): void {
    throw new Error(
      "Not intended to be written outside the context of a PythonFile."
    );
  }

  getFullyQualifiedPath(): string {
    return this.modulePath.join(".");
  }

  getFullyQualifiedModulePath(): string {
    return `${this.getFullyQualifiedPath()}.${this.name}`;
  }
}
