/**
 * Inlined from @fern-api/python-ast/core/Writer
 * This is part of the effort to eject from the python-ast package.
 */

import { AbstractWriter } from "@fern-api/base-generator";
import { Reference } from "@fern-api/python-ast";
import { Config } from "@wasm-fmt/ruff_fmt";

export interface ImportedName {
  name: string;
  isAlias: boolean;
}

/**
 * Writer class for generating Python code with proper indentation and formatting.
 * Extends AbstractWriter from @fern-api/base-generator and adds Python-specific functionality.
 */
export class Writer extends AbstractWriter {
  private fullyQualifiedModulePathsToImportedNames: Record<
    string,
    ImportedName
  > = {};

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
}
