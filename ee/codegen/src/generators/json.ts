import { ValueGenerationError } from "./errors";

import { AstNode } from "src/generators/extensions/ast-node";
import { BoolInstantiation } from "src/generators/extensions/bool-instantiation";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { FloatInstantiation } from "src/generators/extensions/float-instantiation";
import { IntInstantiation } from "src/generators/extensions/int-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Writer } from "src/generators/extensions/writer";

export class Json extends AstNode {
  private readonly astNode: AstNode;

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

  private generateAstNode(value: unknown): AstNode {
    if (value === null || value === undefined) {
      return new NoneInstantiation();
    }

    if (typeof value === "string") {
      return new StrInstantiation(value);
    }

    if (typeof value === "number") {
      if (Number.isInteger(value)) {
        return new IntInstantiation(value);
      }
      return new FloatInstantiation(value);
    }

    if (typeof value === "boolean") {
      return new BoolInstantiation(value);
    }

    if (Array.isArray(value)) {
      return new ListInstantiation(
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
          key: new StrInstantiation(key),
          value: jsonValue,
        };
      });
      return new DictInstantiation(entries, {
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
