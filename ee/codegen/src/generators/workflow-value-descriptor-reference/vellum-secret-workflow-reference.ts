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
                      "Unresolved Vellum secret reference: name is undefined"
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
