import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { VellumVariableType } from "vellum-ai/api/types";

import { OUTPUTS_CLASS_NAME, VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { BaseNode } from "src/generators/nodes/bases/base";
import { TemplatingNode as TemplatingNodeType } from "src/types/vellum";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

const TEMPLATING_INPUT_KEY = "template";
const INPUTS_PREFIX = "inputs";

export class TemplatingNode extends BaseNode<
  TemplatingNodeType,
  TemplatingNodeContext
> {
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    if (nodeInputKey === TEMPLATING_INPUT_KEY) {
      return nodeInputKey;
    }

    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  protected getNodeBaseGenericTypes(): AstNode[] {
    const stateType = this.getStateTypeOrBaseState();
    const primitiveOutputType = this.generateOutputType(
      this.nodeData.data.outputType
    );
    return [stateType, primitiveOutputType];
  }

  protected getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const otherInputs = Array.from(this.nodeInputsByKey.values()).filter(
      (nodeInput) =>
        nodeInput.nodeInputData.id !== this.nodeData.data.templateNodeInputId
    );

    statements.push(
      python.field({
        name: TEMPLATING_INPUT_KEY,
        initializer: this.getTemplatingInput(),
      })
    );

    statements.push(
      python.field({
        name: INPUTS_PREFIX,
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
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
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
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input not found",
          "WARNING"
        )
      );
      return python.TypeInstantiation.str("");
    }

    const templateRule = templatingInput.value.rules[0];
    if (!templateRule) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input rule not found",
          "WARNING"
        )
      );
      return python.TypeInstantiation.str("");
    }

    if (templateRule.type !== "CONSTANT_VALUE") {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input rule is not a constant value",
          "WARNING"
        )
      );
      return python.TypeInstantiation.str("");
    }

    if (templateRule.data.type !== "STRING") {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input rule is not a string",
          "WARNING"
        )
      );
      return python.TypeInstantiation.str("");
    }

    if (!templateRule.data.value) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          "Templating input rule value must be defined and nonempty",
          "WARNING"
        )
      );
      return python.TypeInstantiation.str("");
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
    return outputType === VellumVariableType.Json
      ? python.Type.reference(
          python.reference({
            name: "Json",
            modulePath: [
              ...VELLUM_CLIENT_MODULE_PATH,
              "workflows",
              "types",
              "core",
            ],
          })
        )
      : getVellumVariablePrimitiveType(outputType);
  }
}
