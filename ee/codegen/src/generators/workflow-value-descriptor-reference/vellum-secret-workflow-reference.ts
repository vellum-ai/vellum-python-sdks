import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { AstNode } from "src/generators/extensions/ast-node";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { VellumSecretWorkflowReference as VellumSecretWorkflowReferenceType } from "src/types/vellum";

export class VellumSecretWorkflowReference extends BaseNodeInputWorkflowReference<VellumSecretWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const vellumSecretName =
      this.nodeInputWorkflowReferencePointer.vellumSecretName;

    if (isNil(vellumSecretName)) {
      return python.TypeInstantiation.none();
    }
    return python.instantiateClass({
      classReference: python.reference({
        name: "VellumSecretReference",
        modulePath: [
          ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
          "references",
        ],
      }),
      arguments_: [
        python.methodArgument({
          value: new StrInstantiation(vellumSecretName),
        }),
      ],
    });
  }
}
