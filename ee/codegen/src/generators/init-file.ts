import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BasePersistedFile } from "./base-persisted-file";
import { Comment } from "./extensions/comment";
import { StarImport } from "./extensions/star-import";

export declare namespace InitFile {
  interface Args extends BasePersistedFile.Args {
    modulePath: string[] | Readonly<string[]>;
    statements?: AstNode[];
    imports?: StarImport[];
    comments?: Comment[];
  }
}

export class InitFile extends BasePersistedFile {
  private readonly modulePath: string[];
  private readonly statements: AstNode[];
  private readonly imports: StarImport[] | undefined;
  private readonly comments: Comment[] | undefined;

  public constructor({
    workflowContext,
    modulePath,
    statements,
    imports,
    comments,
  }: InitFile.Args) {
    super({ workflowContext, isInitFile: true });
    this.modulePath = [...modulePath];

    this.statements = statements ?? [];
    this.statements.forEach((statement) => this.inheritReferences(statement));

    this.imports = imports;
    this.imports?.forEach((import_) => this.inheritReferences(import_));

    this.comments = comments;
    this.comments?.forEach((comment) => this.inheritReferences(comment));
  }

  getModulePath(): string[] {
    return this.modulePath;
  }

  public getFileStatements() {
    return this.statements;
  }

  protected getFileImports(): StarImport[] | undefined {
    return this.imports;
  }

  protected getComments(): Comment[] | undefined {
    return this.comments;
  }
}
