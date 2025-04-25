import { writeFile } from "fs/promises";

import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BasePersistedFile } from "./base-persisted-file";

export class ErrorLogFile extends BasePersistedFile {
  protected getFileStatements(): AstNode[] {
    return [];
  }

  protected getModulePath(): string[] {
    return [];
  }

  public async persist(): Promise<void> {
    const errors = this.workflowContext.getErrors("ERROR");
    if (errors.length === 0) {
      return;
    }

    const filePath = this.workflowContext.getAbsolutePath("error.log");
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
