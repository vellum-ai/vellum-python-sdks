import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { VellumVariableType } from "vellum-ai/api/types";

import { OUTPUTS_CLASS_NAME, VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { BaseState } from "src/generators/base-state";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { TemplatingNode as TemplatingNodeType } from "src/types/vellum";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

export class TemplatingNode extends BaseSingleFileNode<
  TemplatingNodeType,
  TemplatingNodeContext
> {
  protected getNodeBaseGenericTypes(): AstNode[] {
    const baseStateClassReference = new BaseState({
      workflowContext: this.workflowContext,
    });

    const primitiveOutputType = this.generateOutputType(
      this.nodeData.data.outputType
    );

    return [baseStateClassReference, primitiveOutputType];
  }

  protected getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const otherInputs = Array.from(this.nodeInputsByKey.values()).filter(
      (nodeInput) =>
        nodeInput.nodeInputData.id !== this.nodeData.data.templateNodeInputId
    );

    statements.push(
      python.field({
        name: "template",
        initializer: this.getTemplatingInput(),
      })
    );

    statements.push(
      python.field({
        name: "inputs",
        initializer: python.TypeInstantiation.dict(
          otherInputs.map((codeInput) => ({
            key: python.TypeInstantiation.str(codeInput.nodeInputData.key),
            value: codeInput,
          })),
          {
            endWithComma: true,
          }
        ),
      })
    );

    return statements;
  }

  protected getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "label",
        initializer: python.TypeInstantiation.str(this.nodeData.data.label),
      })
    );

    statements.push(
      python.field({
        name: "node_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.id),
      })
    );

    statements.push(
      python.field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
      }),
      python.field({
        name: "template_input_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.templateNodeInputId
        ),
      })
    );

    return statements;
  }

  private getTemplatingInput() {
    const templatingInput = this.nodeData.inputs.find(
      (input) => input.id === this.nodeData.data.templateNodeInputId
    );
    if (!templatingInput) {
      throw new NodeAttributeGenerationError(`Templating input not found`);
    }

    const templateRule = templatingInput.value.rules[0];
    if (!templateRule) {
      throw new NodeAttributeGenerationError("Templating input rule not found");
    }

    if (templateRule.type !== "CONSTANT_VALUE") {
      throw new NodeAttributeGenerationError(
        "Templating input rule is not a constant value"
      );
    }

    if (templateRule.data.type !== "STRING") {
      throw new NodeAttributeGenerationError(
        "Templating input rule is not a string"
      );
    }

    if (!templateRule.data.value) {
      throw new NodeAttributeGenerationError(
        "Templating input rule value must be defined and nonempty"
      );
    }

    return python.TypeInstantiation.str(templateRule.data.value, {
      multiline: true,
      startOnNewLine: true,
      endWithNewLine: true,
    });
  }

  protected getOutputDisplay(): python.Field {
    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict([
        {
          key: python.reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [OUTPUTS_CLASS_NAME, "result"],
          }),
          value: python.instantiateClass({
            classReference: python.reference({
              name: "NodeOutputDisplay",
              modulePath:
                this.workflowContext.sdkModulePathNames
                  .NODE_DISPLAY_TYPES_MODULE_PATH,
            }),
            arguments_: [
              python.methodArgument({
                name: "id",
                value: python.TypeInstantiation.uuid(
                  this.nodeData.data.outputId
                ),
              }),
              python.methodArgument({
                name: "name",
                value: python.TypeInstantiation.str("result"),
              }),
            ],
          }),
        },
      ]),
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }

  private generateOutputType(outputType: VellumVariableType): python.Type {
    if (outputType === VellumVariableType.Json) {
      return python.Type.reference(
        python.reference({
          name: "Json",
          modulePath: [
            ...VELLUM_CLIENT_MODULE_PATH,
            "workflows",
            "types",
            "core",
          ],
        })
      );
    }

    const primitiveType = getVellumVariablePrimitiveType(outputType);
    if (primitiveType === undefined) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          `Output type for node ${this.nodeData.id} is not supported and/or not implemented.`,
          "WARNING"
        )
      );
      return python.Type.none();
    }

    return primitiveType;
  }
}
