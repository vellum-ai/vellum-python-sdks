import { AttrPath, ModulePath } from "@fern-api/python-ast/core/types";

import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export declare namespace StarImport {
  interface Args {
    modulePath: ModulePath;
  }
}

export class StarImport extends AstNode {
  readonly name: string;
  readonly modulePath: ModulePath;
  readonly genericTypes: AstNode[];
  readonly alias: string | undefined;
  readonly attribute: AttrPath;
  readonly docs: string | undefined;

  constructor({ modulePath }: StarImport.Args) {
    super();
    this.name = "*";
    this.modulePath = modulePath ?? [];
    this.genericTypes = [];
    this.alias = undefined;
    this.attribute = [];
    this.docs = undefined;
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
