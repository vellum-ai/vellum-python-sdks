import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { NodeInputNotFoundError } from "src/generators/errors";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { WorkflowInputWorkflowReference as WorkflowInputWorkflowReferenceType } from "src/types/vellum";

export class WorkflowInputReference extends BaseNodeInputWorkflowReference<WorkflowInputWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const workflowInputReference = this.nodeInputWorkflowReferencePointer;

    const inputVariableContext =
      this.workflowContext.findInputVariableContextById(
        workflowInputReference.inputVariableId
      );

    if (!inputVariableContext) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find input variable context with id ${workflowInputReference.inputVariableId}`
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
                      `Unresolved input variable reference: id=${workflowInputReference.inputVariableId}`
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
      name: inputVariableContext.definition.name,
      modulePath: inputVariableContext.definition.module,
      attribute: [inputVariableContext.name],
    });
  }
}
