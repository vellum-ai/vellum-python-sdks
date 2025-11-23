import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BasePersistedFile } from "./base-persisted-file";

import { WorkflowContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";

export declare namespace FunctionWithDecorator {
  export interface Args {
    functionSrc: string;
    functionName: string;
    decorator?: python.Decorator;
  }
}

export class FunctionWithDecorator extends AstNode {
  private functionSrc: string;
  private functionName: string;
  private decorator?: python.Decorator;

  constructor(args: FunctionWithDecorator.Args) {
    super();
    this.functionSrc = args.functionSrc;
    this.functionName = args.functionName;
    this.decorator = args.decorator;
  }

  write(writer: Writer): void {
    if (!this.decorator) {
      // No decorator, write the function source directly
      writer.write(this.functionSrc);
      return;
    }

    // Find the position of the specific function definition to insert decorator right before it
    // Match 'def' followed by the function name at the start of a line (possibly with leading whitespace)
    const defMatch = this.functionSrc.match(
      new RegExp(`(\\n|^)(\\s*)def\\s+${this.functionName}\\s*\\(`)
    );

    if (defMatch && defMatch.index !== undefined) {
      // Found the function definition - write everything before it, then decorator, then 'def' and rest
      // defMatch[1] is either '\n' or '' (empty string from ^ anchor)
      const prefixLength = defMatch[1]?.length ?? 0;
      const defStartIndex = defMatch.index + prefixLength;
      const beforeDef = this.functionSrc.substring(0, defStartIndex);
      const defAndAfter = this.functionSrc.substring(defStartIndex);

      // Write content before 'def' (preserving any leading content)
      if (beforeDef.length > 0) {
        writer.write("\n");
      }
      writer.write(beforeDef);

      // Write decorator with proper spacing
      writer.write("\n\n");
      this.decorator.write(writer);

      // Write 'def' and everything after (strip leading newlines to avoid blank line, preserve indentation)
      const trimmedDefAndAfter = defAndAfter.replace(/^\n+/, "");
      writer.write(trimmedDefAndAfter);
    } else {
      // Fallback: if we can't find the function, write decorator then source
      this.decorator.write(writer);
      writer.write("\n");
      writer.write(this.functionSrc);
    }
  }
}

export declare namespace FunctionFile {
  export interface Args {
    workflowContext: WorkflowContext;
    functionSrc: string;
    functionName: string;
    decorator?: python.Decorator;
    modulePath: string[];
  }
}

export class FunctionFile extends BasePersistedFile {
  private readonly functionSrc: string;
  private readonly functionName: string;
  private readonly decorator?: python.Decorator;
  private readonly modulePath: string[];

  constructor({
    workflowContext,
    functionSrc,
    functionName,
    decorator,
    modulePath,
  }: FunctionFile.Args) {
    super({ workflowContext });
    this.functionSrc = functionSrc;
    this.functionName = functionName;
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
      functionName: this.functionName,
      decorator: this.decorator,
    });

    statements.push(functionWithDecorator);

    return statements;
  }
}
