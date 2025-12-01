import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { EnvironmentVariablePointer } from "src/types/vellum";

export class EnvironmentVariablePointerRule extends BaseNodeInputValuePointerRule<EnvironmentVariablePointer> {
  getAstNode(): python.AstNode {
    const envVarName = this.nodeInputValuePointerRule.data.environmentVariable;
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
          value: new StrInstantiation(envVarName),
        }),
      ],
    });
  }
}
