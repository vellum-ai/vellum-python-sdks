import { python } from "@fern-api/python-ast";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { NodeOutputWorkflowReference as NodeOutputWorkflowReferenceType } from "src/types/vellum";

export class NodeOutputWorkflowReference extends BaseNodeInputWorkflowReference<NodeOutputWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const nodeOutputPointer = this.nodeInputWorkflowReferencePointer;

    const nodeContext = this.workflowContext.findNodeContext(
      nodeOutputPointer.nodeId
    );

    if (!nodeContext) {
      return undefined;
    }

    const nodeOutputName = nodeContext.getNodeOutputNameById(
      nodeOutputPointer.nodeOutputId
    );

    if (!nodeOutputName) {
      return undefined;
    }

    if (this.nodeContext && this.nodeContext.isImportedBefore(nodeContext)) {
      return new ClassInstantiation({
        classReference: new Reference({
          name: "LazyReference",
          modulePath: [
            ...this.nodeContext.workflowContext.sdkModulePathNames
              .WORKFLOWS_MODULE_PATH,
            "references",
          ],
        }),
        arguments_: [
          new MethodArgument({
            value: new StrInstantiation(
              `${nodeContext.nodeClassName}.${OUTPUTS_CLASS_NAME}.${nodeOutputName}`
            ),
          }),
        ],
      });
    }

    if (this.nodeContext?.nodeClassName === nodeContext.nodeClassName) {
      return new ClassInstantiation({
        classReference: new Reference({
          name: "LazyReference",
          modulePath: [
            ...this.nodeContext.workflowContext.sdkModulePathNames
              .WORKFLOWS_MODULE_PATH,
            "references",
          ],
        }),
        arguments_: [
          new MethodArgument({
            value: python.lambda({
              body: python.accessAttribute({
                lhs: new Reference({
                  name: nodeContext.nodeClassName,
                  modulePath: [],
                }),
                rhs: new Reference({
                  name: `${OUTPUTS_CLASS_NAME}.${nodeOutputName}`,
                  modulePath: [],
                }),
              }),
            }),
          }),
        ],
      });
    }

    const reference = new Reference({
      name: nodeContext.nodeClassName,
      modulePath: nodeContext.nodeModulePath,
      attribute: [OUTPUTS_CLASS_NAME, nodeOutputName],
    });
    this.inheritReferences(reference);
    return reference;
  }
}
