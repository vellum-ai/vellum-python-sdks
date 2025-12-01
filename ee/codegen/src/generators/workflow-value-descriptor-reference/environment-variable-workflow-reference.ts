import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
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
    return new ClassInstantiation({
      classReference: new Reference({
        name: "EnvironmentVariableReference",
        modulePath: [
          ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
          "references",
        ],
      }),
      arguments_: [
        new MethodArgument({
          name: "name",
          value: new StrInstantiation(environmentVariable),
        }),
      ],
    });
  }
}
