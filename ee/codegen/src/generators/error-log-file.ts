import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BasePersistedFile } from "./base-persisted-file";
import { writeFile } from "fs/promises";
import { join } from "path";

export declare namespace ErrorLogFile {
  interface Args extends BasePersistedFile.Args {}
}

export class ErrorLogFile extends BasePersistedFile {
  protected getFileStatements(): AstNode[] {
    return [];
  }

  protected getModulePath(): string[] {
    return [];
  }

  public async persist(): Promise<void> {
    const errors = this.workflowContext.getErrors();
    if (errors.length === 0) {
      return;
    }

    const filePath = join(
      this.workflowContext.absolutePathToOutputDirectory,
      this.workflowContext.moduleName,
      "error.log"
    );
    const content = errors.map((error) => `- ${error.message}`).join("\n");

    await writeFile(
      filePath,
      `\
Encountered ${errors.length} error(s) while generating code:

${content}
`
    );
  }
}
