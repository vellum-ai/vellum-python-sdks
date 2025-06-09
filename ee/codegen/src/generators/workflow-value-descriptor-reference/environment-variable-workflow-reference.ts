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
      return python.TypeInstantiation.none();
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
