import { python } from "@fern-api/python-ast";

import { ValueGenerationError } from "./errors";

import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export class Json extends AstNode {
  private readonly astNode: python.AstNode;

  constructor(value: unknown) {
    super();

    // Validate that value is JSON serializable
    try {
      JSON.stringify(value);
    } catch {
      throw new ValueGenerationError("Value is not JSON serializable");
    }

    this.astNode = this.generateAstNode(value);
    this.inheritReferences(this.astNode);
  }

  private generateAstNode(value: unknown): python.AstNode {
    if (value === null || value === undefined) {
      return python.TypeInstantiation.none();
    }

    if (typeof value === "string") {
      return python.TypeInstantiation.str(value);
    }

    if (typeof value === "number") {
      if (Number.isInteger(value)) {
        return python.TypeInstantiation.int(value);
      }
      return python.TypeInstantiation.float(value);
    }

    if (typeof value === "boolean") {
      return python.TypeInstantiation.bool(value);
    }

    if (Array.isArray(value)) {
      return python.TypeInstantiation.list(
        value.map((item) => {
          const jsonValue = new Json(item);
          this.inheritReferences(jsonValue);
          return jsonValue;
        }),
        {
          endWithComma: true,
        }
      );
    }

    if (typeof value === "object") {
      const entries = Object.entries(value).map(([key, val]) => {
        const jsonValue = new Json(val);
        this.inheritReferences(jsonValue);

        return {
          key: python.TypeInstantiation.str(key),
          value: jsonValue,
        };
      });
      return python.TypeInstantiation.dict(entries, {
        endWithComma: true,
      });
    }

    throw new ValueGenerationError(
      `Unsupported JSON value type: ${typeof value}`
    );
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
