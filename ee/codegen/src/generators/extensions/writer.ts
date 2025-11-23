/**
 * Inlined from @fern-api/python-ast/core/Writer
 * This is part of the effort to eject from the python-ast package.
 */

import { Reference } from "@fern-api/python-ast";
import { Config } from "@wasm-fmt/ruff_fmt";

export interface ImportedName {
  name: string;
  isAlias: boolean;
}

export interface AbstractAstNode {
  write(writer: Writer): void;
}

const TAB_SIZE = 4;

/**
 * Writer class for generating Python code with proper indentation and formatting.
 * Combines functionality from AbstractWriter and Writer from @fern-api/python-ast.
 */
export class Writer {
  /* The contents being written */
  buffer = "";
  /* Indentation level (multiple of 4) */
  private indentLevel = 0;
  /* Whether anything has been written to the buffer */
  private hasWrittenAnything = false;
  /* Whether the last character written was a newline */
  private lastCharacterIsNewline = false;
  /* Map of fully qualified module paths to imported names */
  private fullyQualifiedModulePathsToImportedNames: Record<
    string,
    ImportedName
  > = {};

  /**
   * Writes arbitrary text with proper indentation
   * @param text
   */
  write(text: string): void {
    const textEndsInNewline = text.length > 0 && text.endsWith("\n");
    // temporarily remove the trailing newline, since we don't want to add the indent prefix after it
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

  /**
   * Writes arbitrary text without indentation
   * @param text
   */
  writeNoIndent(text: string): void {
    const currIndentLevel = this.indentLevel;
    this.indentLevel = 0;
    this.write(text);
    this.indentLevel = currIndentLevel;
  }

  /**
   * Writes a node
   * @param node
   */
  writeNode(node: AbstractAstNode): void {
    node.write(this);
  }

  /**
   * Writes a node but then suffixes with a `;` and new line
   * @param node
   */
  writeNodeStatement(node: AbstractAstNode): void {
    node.write(this);
    this.write(";");
    this.writeNewLineIfLastLineNot();
  }

  /**
   * Writes text but then suffixes with a `;`
   * @param text
   */
  writeTextStatement(text: string): void {
    this.writeCodeBlock(text);
    this.write(";");
    this.writeNewLineIfLastLineNot();
  }

  /**
   * Writes text but then suffixes with a `;`
   * @param prefix
   * @param statement
   */
  controlFlow(prefix: string, statement: AbstractAstNode): void {
    this.writeCodeBlock(prefix);
    this.write(" (");
    this.writeNode(statement);
    this.write(") {");
    this.writeNewLineIfLastLineNot();
    this.indent();
  }

  /**
   * Writes text but then suffixes with a `;`
   */
  endControlFlow(): void {
    this.dedent();
    this.writeLine("}");
  }

  /**
   * Please try to not use this. It is here for swift.
   * @param titles
   * @param openingCharacter
   * @param callback
   * @param closingCharacter
   */
  openBlock(
    titles: (string | undefined)[],
    openingCharacter: string | undefined = "{",
    callback: () => void,
    closingCharacter: string | undefined = "}"
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

  /* Only writes a newline if last line in the buffer is not a newline */
  writeLine(text = ""): void {
    this.write(text);
    this.writeNewLineIfLastLineNot();
  }

  /* Always writes newline */
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

  /**
   * Set reference name overrides for import management
   * @param completeRefPathsToNameOverrides
   */
  setRefNameOverrides(
    completeRefPathsToNameOverrides: Record<string, ImportedName>
  ): void {
    this.fullyQualifiedModulePathsToImportedNames =
      completeRefPathsToNameOverrides;
  }

  /**
   * Clear reference name overrides
   */
  unsetRefNameOverrides(): void {
    this.fullyQualifiedModulePathsToImportedNames = {};
  }

  /**
   * Get the import name override for a reference
   * @param reference
   */
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

  /**
   * Convert buffer to string
   */
  toString(): string {
    return this.buffer;
  }

  /**
   * Convert buffer to formatted string using ruff
   * @param config
   */
  async toStringFormatted(config?: Config): Promise<string> {
    const { default: init, format } = await import("@wasm-fmt/ruff_fmt");
    await init();
    return format(this.buffer, undefined, config);
  }

  /*******************************
   * Helper Methods
   *******************************/

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

  /**
   * Helper method to write a code block (inlined from CodeBlock class)
   * @param value
   */
  private writeCodeBlock(value: string | ((writer: Writer) => void)): void {
    if (typeof value === "string") {
      this.write(value);
    } else {
      value(this);
    }
  }
}
