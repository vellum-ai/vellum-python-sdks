import { isNil } from "lodash";

import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { VellumSecretWorkflowReference as VellumSecretWorkflowReferenceType } from "src/types/vellum";

export class VellumSecretWorkflowReference extends BaseNodeInputWorkflowReference<VellumSecretWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const vellumSecretName =
      this.nodeInputWorkflowReferencePointer.vellumSecretName;

    if (isNil(vellumSecretName)) {
      return new NoneInstantiation();
    }
    return new ClassInstantiation({
      classReference: new Reference({
        name: "VellumSecretReference",
        modulePath: [
          ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
          "references",
        ],
      }),
      arguments_: [
        new MethodArgument({
          value: new StrInstantiation(vellumSecretName),
        }),
      ],
    });
  }
}
