import { Decorator } from "@fern-api/python-ast/Decorator";
import { Reference } from "@fern-api/python-ast/Reference";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { CustomComment } from "./custom-comment";

export declare namespace CustomClass {
  interface Args {
    name: string;
    docs?: string;
    extends_?: Reference[];
    decorators?: Decorator[];
  }
}

export class CustomClass extends AstNode {
  private readonly name: string;
  private readonly docs?: string;
  private readonly extends_?: Reference[];
  private readonly decorators?: Decorator[];
  private readonly children: AstNode[] = [];

  constructor({ name, docs, extends_, decorators }: CustomClass.Args) {
    super();
    this.name = name;
    this.docs = docs;
    this.extends_ = extends_;
    this.decorators = decorators;

    if (extends_) {
      extends_.forEach((extend) => this.inheritReferences(extend));
    }
    if (decorators) {
      decorators.forEach((decorator) => this.inheritReferences(decorator));
    }
  }

  public add(child: AstNode): void {
    this.children.push(child);
    this.inheritReferences(child);
  }

  public write(writer: Writer): void {
    if (this.decorators) {
      this.decorators.forEach((decorator) => {
        decorator.write(writer);
        writer.newLine();
      });
    }

    writer.write("class ");
    writer.write(this.name);

    if (this.extends_ && this.extends_.length > 0) {
      writer.write("(");

      const extends_ = this.extends_;
      extends_.forEach((extend, index) => {
        extend.write(writer);
        if (index < extends_.length - 1) {
          writer.write(", ");
        }
      });

      writer.write(")");
    }

    writer.write(":");
    writer.newLine();
    writer.indent();

    if (this.docs) {
      const comment = new CustomComment({ docs: this.docs });
      comment.write(writer);
      writer.newLine();
    }

    if (this.children.length > 0) {
      this.children.forEach((child, index) => {
        child.write(writer);
        if (index < this.children.length - 1) {
          writer.newLine();
        }
      });
    } else {
      writer.write("pass");
      writer.newLine();
    }

    writer.dedent();
  }
}
