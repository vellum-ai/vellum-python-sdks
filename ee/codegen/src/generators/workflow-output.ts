import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { WorkflowContext } from "src/context";
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import { toSnakeCase } from "src/utils/casing";

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
    const terminalNodeId = this.workflowOutputContext.getFinalOutputNodeId();
    const terminalNodeContext =
      this.workflowContext.getNodeContext(terminalNodeId);

    const workflowOutput = python.field({
      name: toSnakeCase(this.workflowOutputContext.getOutputName()),
      initializer: python.reference({
        name: terminalNodeContext.nodeClassName,
        modulePath: terminalNodeContext.nodeModulePath,
        attribute: [OUTPUTS_CLASS_NAME, "value"],
      }),
    });

    this.inheritReferences(workflowOutput);

    return workflowOutput;
  }

  write(writer: Writer): void {
    this.workflowOutput.write(writer);
  }
}
