import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { EnvironmentVariableWorkflowReference as EnvironmentVariableWorkflowReferenceType } from "src/types/vellum";

export class EnvironmentVariableWorkflowReference extends BaseNodeInputWorkflowReference<EnvironmentVariableWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const environmentVariable =
      this.nodeInputWorkflowReferencePointer.environmentVariable;

    if (isNil(environmentVariable)) {
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
                      "Unresolved environment variable reference: name is undefined"
                    ),
                  }),
                ],
              }),
            }),
          }),
        ],
      });
    }
    return python.instantiateClass({
      classReference: python.reference({
        name: "EnvironmentVariableReference",
        modulePath: [
          ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
          "references",
        ],
      }),
      arguments_: [
        python.methodArgument({
          name: "name",
          value: python.TypeInstantiation.str(environmentVariable),
        }),
      ],
    });
  }
}
