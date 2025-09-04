import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { BasePersistedFile } from "./base-persisted-file";

import { WorkflowContext } from "src/context";

export declare namespace FunctionWithDecorator {
  export interface Args {
    functionSrc: string;
    decorator?: python.Decorator;
  }
}

export class FunctionWithDecorator extends AstNode {
  private functionSrc: string;
  private decorator?: python.Decorator;

  constructor(args: FunctionWithDecorator.Args) {
    super();
    this.functionSrc = args.functionSrc;
    this.decorator = args.decorator;
  }

  write(writer: Writer): void {
    // Write decorator if present
    if (this.decorator) {
      writer.write("\n\n");
      this.decorator.write(writer);
    }

    // Write the function source directly
    writer.write(this.functionSrc);
  }
}

export declare namespace FunctionFile {
  export interface Args {
    workflowContext: WorkflowContext;
    functionSrc: string;
    decorator?: python.Decorator;
    modulePath: string[];
  }
}

export class FunctionFile extends BasePersistedFile {
  private readonly functionSrc: string;
  private readonly decorator?: python.Decorator;
  private readonly modulePath: string[];

  constructor({
    workflowContext,
    functionSrc,
    decorator,
    modulePath,
  }: FunctionFile.Args) {
    super({ workflowContext });
    this.functionSrc = functionSrc;
    this.decorator = decorator;
    this.modulePath = modulePath;

    if (this.decorator) {
      this.inheritReferences(this.decorator);
    }
  }

  protected getModulePath(): string[] {
    return this.modulePath;
  }

  protected getFileStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const functionWithDecorator = new FunctionWithDecorator({
      functionSrc: this.functionSrc,
      decorator: this.decorator,
    });

    statements.push(functionWithDecorator);

    return statements;
  }
}
