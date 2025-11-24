import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";

import { WorkflowValueDescriptor } from "./workflow-value-descriptor";

import { WorkflowContext } from "src/context";
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export declare namespace WorkflowOutput {
  export interface Args {
    workflowContext: WorkflowContext;
    workflowOutputContext: WorkflowOutputContext;
  }
}

export class WorkflowOutput extends AstNode {
  private workflowContext: WorkflowContext;
  private workflowOutputContext: WorkflowOutputContext;
  private workflowOutput: Field | undefined;

  public constructor(args: WorkflowOutput.Args) {
    super();

    this.workflowContext = args.workflowContext;
    this.workflowOutputContext = args.workflowOutputContext;

    this.workflowOutput = this.generateWorkflowOutput();
  }

  private generateWorkflowOutput(): Field | undefined {
    const outputVariable = this.workflowOutputContext.getOutputVariable();
    if (!outputVariable) {
      return undefined;
    }

    const workflowOutput = python.field({
      name: outputVariable.name,
      initializer: new WorkflowValueDescriptor({
        workflowContext: this.workflowContext,
        workflowValueDescriptor:
          this.workflowOutputContext.getWorkflowValueDescriptor(),
      }),
    });

    this.inheritReferences(workflowOutput);

    return workflowOutput;
  }

  write(writer: Writer): void {
    if (this.workflowOutput) {
      this.workflowOutput.write(writer);
    }
  }
}
