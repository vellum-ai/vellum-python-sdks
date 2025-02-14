import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { WorkflowValueDescriptor } from "./workflow-value-descriptor";

import { WorkflowContext } from "src/context";
import { WorkflowOutputContext } from "src/context/workflow-output-context";

export declare namespace WorkflowOutput {
  export interface Args {
    workflowContext: WorkflowContext;
    workflowOutputContext: WorkflowOutputContext;
  }
}

export class WorkflowOutput extends AstNode {
  private workflowContext: WorkflowContext;
  private workflowOutputContext: WorkflowOutputContext;
  private workflowOutput: Field;

  public constructor(args: WorkflowOutput.Args) {
    super();

    this.workflowContext = args.workflowContext;
    this.workflowOutputContext = args.workflowOutputContext;

    this.workflowOutput = this.generateWorkflowOutput();
  }

  private generateWorkflowOutput(): Field {
    const workflowOutput = python.field({
      name: this.workflowOutputContext.getOutputVariable().name,
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
    this.workflowOutput.write(writer);
  }
}
