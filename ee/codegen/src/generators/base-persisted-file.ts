import { mkdir, writeFile } from "fs/promises";
import path, { join } from "path";

import { Comment } from "@fern-api/python-ast/Comment";
import { Reference } from "@fern-api/python-ast/Reference";
import { StarImport } from "@fern-api/python-ast/StarImport";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { ModulePath } from "@fern-api/python-ast/core/types";

import { INIT_FILE_NAME } from "src/constants";
import { WorkflowContext } from "src/context";
import { FileFormattingError } from "src/generators/errors";
import { PythonFile } from "src/generators/extensions";

export declare namespace BasePersistedFile {
  interface Args {
    workflowContext: WorkflowContext;
    isInitFile?: boolean;
  }
}

const VELLUM_MODULES = new Set(["vellum", "vellum_ee"]);

class ImportSortedPythonFile extends PythonFile {
  writeImports({
    writer,
    uniqueReferences,
  }: {
    writer: Writer;
    uniqueReferences: Map<
      string,
      { modulePath: ModulePath; references: Reference[] }
    >;
  }) {
    const sortedReferences = this.sortReferences(uniqueReferences);
    let lastPriority: number | null = null;

    for (const {
      fullyQualifiedPath,
      modulePath,
      references,
      priority,
    } of sortedReferences) {
      const refModulePath = modulePath;
      // Check to see if the reference is defined in this same file and if so, skip its import
      if (this.isDefinedInFile(refModulePath)) {
        continue;
      }

      if (priority !== lastPriority) {
        if (lastPriority !== null) {
          writer.newLine();
        }
        lastPriority = priority;
      }

      if (refModulePath[0] === this.path[0]) {
        // Relativize the import
        // Calculate the common prefix length
        let commonPrefixLength = 0;
        while (
          commonPrefixLength < this.path.length &&
          commonPrefixLength < refModulePath.length &&
          this.path[commonPrefixLength] === refModulePath[commonPrefixLength]
        ) {
          commonPrefixLength++;
        }
        // Calculate the number of levels to go up
        let levelsUp = this.path.length - commonPrefixLength;
        // If this is an __init__.py file, then we must go one more level up.
        if (this.isInitFile) {
          levelsUp++;
        }
        // Build the relative import path
        let relativePath = levelsUp > 0 ? ".".repeat(levelsUp) : ".";
        relativePath += refModulePath.slice(commonPrefixLength).join(".");
        // Write the relative import statement
        writer.write(
          `from ${relativePath} import ${references
            .map((reference) => this.getImportName({ writer, reference }))
            .join(", ")}`
        );
      } else {
        // Use fully qualified path
        writer.write(
          `from ${fullyQualifiedPath} import ${references
            .map((reference) => this.getImportName({ writer, reference }))
            .join(", ")}`
        );
      }
      writer.newLine();
    }
    if (Object.keys(uniqueReferences).length > 0) {
      writer.newLine();
    }
  }

  // The above logic is copied and pasted from the Fern PythonFile AST Library
  // The below is our only contribution to the class
  private sortReferences(
    uniqueReferences: Map<
      string,
      { modulePath: ModulePath; references: Reference[] }
    >
  ) {
    return Array.from(uniqueReferences.entries())
      .map(([fullyQualifiedPath, { modulePath, references }]) => ({
        fullyQualifiedPath,
        modulePath,
        references: references.sort(),
        priority: this.getModulePathPriority(modulePath),
      }))
      .sort((a, b) => {
        if (a.priority !== b.priority) {
          return b.priority - a.priority;
        }
        if (a.references[0]?.name === "*" && b.references[0]?.name !== "*") {
          return 1;
        }
        if (b.references[0]?.name === "*" && a.references[0]?.name !== "*") {
          return -1;
        }
        return a.modulePath.join(".").localeCompare(b.modulePath.join("."));
      });
  }

  private getModulePathPriority(modulePath: ModulePath) {
    if (!modulePath[0]) {
      return 0;
    }

    if (modulePath[0] === this.path[0]) {
      return 1;
    }

    if (VELLUM_MODULES.has(modulePath[0])) {
      return 2;
    }

    return 3;
  }
}

export abstract class BasePersistedFile extends AstNode {
  protected readonly workflowContext: WorkflowContext;
  protected readonly isInitFile: boolean;

  public constructor({ workflowContext, isInitFile }: BasePersistedFile.Args) {
    super();
    this.workflowContext = workflowContext;
    this.isInitFile = isInitFile ?? false;
  }

  protected abstract getModulePath(): string[];

  protected abstract getFileStatements(): AstNode[] | undefined;

  protected getFileImports(): StarImport[] | undefined {
    return undefined;
  }

  protected getComments(): Comment[] | undefined {
    return undefined;
  }

  public write(writer: Writer): void {
    const fileStatements = this.getFileStatements();
    if (!fileStatements) {
      return;
    }

    const file = new ImportSortedPythonFile({
      path: this.getModulePath(),
      isInitFile: this.isInitFile,
      statements: fileStatements,
      imports: this.getFileImports(),
      comments: this.getComments(),
    });

    file.inheritReferences(this);

    file.write(writer);
  }

  public async persist(): Promise<void> {
    const absolutePathToModuleDirectory =
      this.workflowContext.absolutePathToOutputDirectory;

    const modulePath = this.getModulePath();

    let fileName: string;
    let filePath: string[];
    if (this.isInitFile) {
      fileName = INIT_FILE_NAME;
      filePath = modulePath;
    } else {
      fileName = modulePath[modulePath.length - 1] + ".py";
      filePath = modulePath.slice(0, -1);
    }

    const filepath = join(absolutePathToModuleDirectory, ...filePath, fileName);
    await mkdir(path.dirname(filepath), { recursive: true });

    const writer = new Writer();
    this.write(writer);

    let contents: string;
    try {
      contents = await writer.toStringFormatted({ line_width: 120 });
      contents = this.postprocessDocstrings(contents);
    } catch (error) {
      if (error instanceof Error) {
        console.error(`Error formatting ${fileName}:`, error);
      } else {
        console.error(
          new FileFormattingError(
            `Error formatting ${fileName}: ${String(error)}`,
            { cause: error }
          )
        );
      }
      contents = writer.toString();
    }

    await writeFile(filepath, contents);
  }

  private postprocessDocstrings(content: string): string {
    // Find an escaped quote followed by space(s) right before closing triple quotes
    const fixPattern = /(\\")(\s)(""")/g;

    // Remove the extra space between escaped quote and closing triple quotes
    return content.replace(fixPattern, "$1$3");
  }
}
