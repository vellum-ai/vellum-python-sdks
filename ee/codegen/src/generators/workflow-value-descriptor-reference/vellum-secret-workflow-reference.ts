import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

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
          value: python.TypeInstantiation.str(vellumSecretName),
        }),
      ],
    });
  }
}
