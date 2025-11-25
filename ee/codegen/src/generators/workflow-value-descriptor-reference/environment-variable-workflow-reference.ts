import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { AstNode } from "src/generators/extensions/ast-node";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
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
          value: new StrInstantiation(environmentVariable),
        }),
      ],
    });
  }
}
