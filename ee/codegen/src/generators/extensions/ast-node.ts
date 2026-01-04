import { Writer } from "./writer";

import type { Reference } from "./reference";
import type { Config } from "@wasm-fmt/ruff_fmt";

export abstract class AstNode {
  protected references: Reference[] = [];

  abstract write(writer: Writer): void;

  addReference(reference: Reference): void {
    this.references.push(reference);
  }

  inheritReferences(astNode: AstNode | undefined): void {
    if (astNode === undefined) {
      return;
    }
    astNode.references.forEach((reference) => {
      if (!this.references.includes(reference)) {
        this.addReference(reference);
      }
    });
  }

  getReferences(): Reference[] {
    return this.references;
  }

  toString(): string {
    const writer = new Writer();
    this.write(writer);
    return writer.toString();
  }

  async toStringFormatted(config?: Config): Promise<string> {
    const writer = new Writer();
    this.write(writer);
    return await writer.toStringFormatted(config);
  }
}
