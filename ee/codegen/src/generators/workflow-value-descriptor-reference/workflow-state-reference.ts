import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputWorkflowReference } from "./BaseNodeInputWorkflowReference";

import { NodeInputNotFoundError } from "src/generators/errors";
import { WorkflowStateVariableWorkflowReference as WorkflowStateVariableWorkflowReferenceType } from "src/types/vellum";

export class WorkflowStateReference extends BaseNodeInputWorkflowReference<WorkflowStateVariableWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const workflowStateReference = this.nodeInputWorkflowReferencePointer;

    const stateVariableContext =
      this.workflowContext.findStateVariableContextById(
        workflowStateReference.stateVariableId
      );

    if (!stateVariableContext) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find state variable context with id ${workflowStateReference.stateVariableId}`,
          "WARNING"
        )
      );
      // Return a LazyReference with error message instead of None to provide better error context
      return python.instantiateClass({
        classReference: python.reference({
          name: "LazyReference",
          modulePath: [
            ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
            "references",
          ],
        }),
        arguments_: [
          python.methodArgument({
            value: python.lambda({
              body: python.instantiateClass({
                classReference: python.reference({
                  name: "ValueError",
                  modulePath: [],
                }),
                arguments_: [
                  python.methodArgument({
                    value: python.TypeInstantiation.str(
                      `Unresolved state variable reference: id=${workflowStateReference.stateVariableId}`
                    ),
                  }),
                ],
              }),
            }),
          }),
        ],
      });
    }
    return python.reference({
      name: stateVariableContext.definition.name,
      modulePath: stateVariableContext.definition.module,
      attribute: [stateVariableContext.name],
    });
  }
}
