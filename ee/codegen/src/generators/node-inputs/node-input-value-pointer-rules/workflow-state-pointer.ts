import { BaseNodeInputValuePointerRule } from "./base";

import { BaseNodeContext } from "src/context/node-context/base";
import { NodeInputNotFoundError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { WorkflowDataNode, WorkflowStatePointer } from "src/types/vellum";

export declare namespace WorkflowStatePointerRule {
  interface Args {
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    nodeInputValuePointerRule: WorkflowStatePointer;
  }
}

export class WorkflowStatePointerRule extends BaseNodeInputValuePointerRule<WorkflowStatePointer> {
  constructor(args: WorkflowStatePointerRule.Args) {
    super(args);
  }

  getAstNode(): AstNode {
    const workflowStatePointerRuleData = this.nodeInputValuePointerRule.data;

    const stateVariableContext =
      this.workflowContext.findStateVariableContextById(
        workflowStatePointerRuleData.stateVariableId
      );

    if (!stateVariableContext) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find state variable context with id ${workflowStatePointerRuleData.stateVariableId}`,
          "WARNING"
        )
      );
      return new NoneInstantiation();
    }

    return new Reference({
      name: stateVariableContext.definition.name,
      modulePath: stateVariableContext.definition.module,
      attribute: [stateVariableContext.name],
    });
  }
}
