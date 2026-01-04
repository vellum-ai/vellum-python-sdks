import type { AstNode } from "./ast-node";
import type { Reference } from "./reference";
import type { Config } from "@wasm-fmt/ruff_fmt";

export interface ImportedName {
  name: string;
  isAlias?: boolean;
}

const TAB_SIZE = 4;

export class Writer {
  buffer: string = "";
  private indentLevel: number = 0;
  private hasWrittenAnything: boolean = false;
  private lastCharacterIsNewline: boolean = false;
  private fullyQualifiedModulePathsToImportedNames: Record<
    string,
    ImportedName
  > = {};

  setRefNameOverrides(
    completeRefPathsToNameOverrides: Record<string, ImportedName>
  ): void {
    this.fullyQualifiedModulePathsToImportedNames =
      completeRefPathsToNameOverrides;
  }

  unsetRefNameOverrides(): void {
    this.fullyQualifiedModulePathsToImportedNames = {};
  }

  getRefNameOverride(reference: Reference): ImportedName {
    const explicitNameOverride =
      this.fullyQualifiedModulePathsToImportedNames[
        reference.getFullyQualifiedModulePath()
      ];
    if (explicitNameOverride) {
      return explicitNameOverride;
    }
    return {
      name: reference.alias ?? reference.name,
      isAlias: !!reference.alias,
    };
  }

  write(text: string): void {
    const textEndsInNewline = text.length > 0 && text.endsWith("\n");
    const textWithoutNewline = textEndsInNewline
      ? text.substring(0, text.length - 1)
      : text;
    const indent = this.getIndentString();
    let indentedText = textWithoutNewline.replaceAll("\n", `\n${indent}`);
    if (this.isAtStartOfLine()) {
      indentedText = indent + indentedText;
    }
    if (textEndsInNewline) {
      indentedText += "\n";
    }
    this.writeInternal(indentedText);
  }

  writeNoIndent(text: string): void {
    const currIndentLevel = this.indentLevel;
    this.indentLevel = 0;
    this.write(text);
    this.indentLevel = currIndentLevel;
  }

  writeNode(node: AstNode): void {
    node.write(this);
  }

  writeNodeStatement(node: AstNode): void {
    node.write(this);
    this.write(";");
    this.writeNewLineIfLastLineNot();
  }

  writeTextStatement(text: string): void {
    this.write(text);
    this.write(";");
    this.writeNewLineIfLastLineNot();
  }

  controlFlow(prefix: string, statement: AstNode): void {
    this.write(prefix);
    this.write(" (");
    this.writeNode(statement);
    this.write(") {");
    this.writeNewLineIfLastLineNot();
    this.indent();
  }

  endControlFlow(): void {
    this.dedent();
    this.writeLine("}");
  }

  openBlock(
    titles: (string | undefined)[],
    openingCharacter: string | undefined,
    callback: () => void,
    closingCharacter?: string | undefined
  ): void {
    const filteredTitles = titles
      .filter((title) => title !== undefined)
      .join(" ");
    if (filteredTitles) {
      this.write(`${filteredTitles} ${openingCharacter ?? ""}`);
    } else {
      this.write(openingCharacter ?? "");
    }
    try {
      this.indent();
      callback();
      this.dedent();
    } finally {
      this.write(closingCharacter ?? "");
    }
  }

  writeLine(text: string = ""): void {
    this.write(text);
    this.writeNewLineIfLastLineNot();
  }

  newLine(): void {
    this.writeInternal("\n");
  }

  writeNewLineIfLastLineNot(): void {
    if (!this.lastCharacterIsNewline) {
      this.writeInternal("\n");
    }
  }

  indent(): void {
    this.indentLevel++;
  }

  dedent(): void {
    this.indentLevel--;
  }

  toString(): string {
    return this.buffer;
  }

  async toStringFormatted(config?: Config): Promise<string> {
    const { default: init, format } = await import("@wasm-fmt/ruff_fmt");
    await init();
    return format(this.buffer, undefined, config);
  }

  private writeInternal(text: string): string {
    if (text.length > 0) {
      this.hasWrittenAnything = true;
      this.lastCharacterIsNewline = text.endsWith("\n");
    }
    return (this.buffer += text);
  }

  private isAtStartOfLine(): boolean {
    return this.lastCharacterIsNewline || !this.hasWrittenAnything;
  }

  private getIndentString(): string {
    return " ".repeat(this.indentLevel * TAB_SIZE);
  }
}
