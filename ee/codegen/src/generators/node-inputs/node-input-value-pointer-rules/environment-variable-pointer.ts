import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { EnvironmentVariablePointer } from "src/types/vellum";

export class EnvironmentVariablePointerRule extends BaseNodeInputValuePointerRule<EnvironmentVariablePointer> {
  getAstNode(): python.AstNode {
    const envVarName = this.nodeInputValuePointerRule.data.environmentVariable;
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
          value: python.TypeInstantiation.str(envVarName),
        }),
      ],
    });
  }
}
