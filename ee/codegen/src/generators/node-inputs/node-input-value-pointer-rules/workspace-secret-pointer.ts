import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { BaseNodeInputValuePointerRule } from "./base";

import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { WorkspaceSecretPointer as WorkspaceSecretPointerType } from "src/types/vellum";

export class WorkspaceSecretPointerRule extends BaseNodeInputValuePointerRule<WorkspaceSecretPointerType> {
  getAstNode(): python.AstNode {
    const workspaceSecretPointerData = this.nodeInputValuePointerRule.data;

    if (!workspaceSecretPointerData.workspaceSecretId) {
      return python.TypeInstantiation.none();
    }

    const workspaceSecretName = this.workflowContext.getWorkspaceSecretName(
      workspaceSecretPointerData.workspaceSecretId
    );

    if (isNil(workspaceSecretName)) {
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
          value: new StrInstantiation(workspaceSecretName),
        }),
      ],
    });
  }
}
