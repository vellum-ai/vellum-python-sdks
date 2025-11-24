import { AstNode } from "./ast-node";
import { Writer } from "./writer";

export type ModulePath = string[] | Readonly<string[]>;
export type AttrPath = string[] | Readonly<string[]>;

export declare namespace Reference {
  interface Args {
    name: string;
    modulePath?: ModulePath;
    genericTypes?: AstNode[];
    alias?: string;
    attribute?: AttrPath;
  }
}

export class Reference extends AstNode {
  readonly name: string;
  readonly modulePath: ModulePath;
  readonly genericTypes: AstNode[];
  readonly alias: string | undefined;
  readonly attribute: AttrPath;

  constructor({
    name,
    modulePath,
    genericTypes,
    alias,
    attribute,
  }: Reference.Args) {
    super();
    this.name = name;
    this.modulePath = modulePath ?? [];
    this.genericTypes = genericTypes ?? [];
    this.alias = alias;
    this.attribute = attribute ?? [];

    this.references.push(this);
    this.genericTypes.forEach((genericType) => {
      this.inheritReferences(genericType);
    });
  }

  write(writer: Writer): void {
    const nameOverride = writer.getRefNameOverride(this);
    writer.write(nameOverride.name);

    if (this.genericTypes.length > 0) {
      writer.write("[");
      this.genericTypes.forEach((genericType, index) => {
        if (index > 0) {
          writer.write(", ");
        }
        genericType.write(writer);
      });
      writer.write("]");
    }

    if (this.attribute.length > 0) {
      writer.write(".");
      this.attribute.forEach((attr, index) => {
        if (index > 0) {
          writer.write(".");
        }
        writer.write(attr);
      });
    }
  }

  getFullyQualifiedPath(): string {
    return this.modulePath.join(".");
  }

  getFullyQualifiedModulePath(): string {
    return `${this.getFullyQualifiedPath()}.${this.name}`;
  }
}
